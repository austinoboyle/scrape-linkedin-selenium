from .Scraper import Scraper
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

import time
from .utils import *


class ConnectionScraper(Scraper):
    """
    Scraper for Personal LinkedIn Profiles. See inherited Scraper class for
    details about the constructor.
    """

    def __init__(self, first_only=True, *args, **kwargs):
        super(ConnectionScraper, self).__init__(*args, **kwargs)
        self.first_only = first_only

    def scrape(self, url='', user=None):
        self.load_profile_page(url, user)
        return self.get_first_connections()

    def load_profile_page(self, url='', user=None):
        """Load profile page and all async content

        Params:
            - url {str}: url of the profile to be loaded
        Raises:
            ValueError: If link doesn't match a typical profile url
        """
        if user:
            url = 'http://www.linkedin.com/in/' + user
        if 'com/in/' not in url:
            raise ValueError("Url must look like ...linkedin.com/in/NAME")
        self.current_profile = url.split(r'com/in/')[1]
        self.driver.get(url)
        # Wait for page to load dynamically via javascript
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.pv-top-card-section')),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.profile-unavailable'))
            ))
        except TimeoutException as e:
            raise Exception(
                """Took too long to load profile.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor""")

        # Check if we got the 'profile unavailable' page
        try:
            self.driver.find_element_by_css_selector('.pv-top-card-section')
        except:
            raise ValueError(
                'Profile Unavailable: Profile link does not match any current Linkedin Profiles')

    def get_first_connections(self):
        try:
            see_connections_link = WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                '.pv-top-card-v2-section__link--connections'
            )))
        except TimeoutException as e:
            print("""Took too long to load connections link. This usually indicates you were trying to
scrape the connections of someone you aren't connected to.""")
            return []

        see_connections_link.click()
        try:
            self.configure_connection_type()
        except TimeoutException:
            return []
        all_conns = []

    def next_page(self):
        next_btn = self.driver.find_element_by_css_selector('button.next')
        next_btn.click()
        self.wait(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '.results-paginator li.page-list li.active'), str(self.page_num + 1)
        ))
        self.page_num += 1

    def scrape_all_pages(self):
        self.page_num = 1
        all_results = []
        more_pages = True
        while more_pages:
            more_pages, page_results = self.scrape_page()
            all_results += page_results
            if more_pages:
                self.next_page()
        return all_results

    def scrape_page(self):
        print("SCRAPING PAGE: ", self.page_num)
        self.scroll_to_bottom()
        try:
            next_btn = self.driver.find_element_by_css_selector('button.next')
        except NoSuchElementException:
            next_btn = None
        connections = self.driver.find_elements_by_css_selector(
            '.search-entity')
        results = []
        for conn in connections:
            result = {}
            result['name'] = conn.find_element_by_css_selector(
                '.actor-name').text
            link = conn.find_element_by_css_selector(
                '.search-result__result-link').get_attribute('href')
            user_id = re.search(r'/in/(.*?)/', link).group(1)
            result['id'] = user_id
            results.append(result)
        return bool(next_btn), results

    def configure_connection_type(self):
        dropdown_btn = self.wait_for_el(
            '.search-s-facet--facetNetwork form button')
        if not self.first_only:
            return
        new_url = re.sub(r'&facetNetwork=(.*?)&',
                         r'&facetNetwork=%5B"F"%5D&', self.driver.current_url)
        self.driver.get(new_url)
        self.wait(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '.search-s-facet--facetNetwork'), '1st'
        ))
