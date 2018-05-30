from .Scraper import Scraper
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
import time
from .utils import AnyEC
from bs4 import BeautifulSoup
import os
from .Job import Job

class SplitViewJobScraper(Scraper):
    """
    Scraper that consolidates the JobSearchScraper and JobScraper classes.
    Made in response to LinkedIn adding a split view interface. See inherited Scraper class for details.
    """

    def scrape(self, url='', job_id=None):
        self.load_job(url,job_id)
        
        # Get basic info
        basics_html = self.driver.find_element_by_css_selector(
            '.jobs-details-top-card').get_attribute('outerHTML')

        # Get detailed info
        details_html = self.driver.find_element_by_css_selector(
            '.jobs-description__container').get_attribute('outerHTML')

        return Job(job_id,basics_html,details_html)

    def load_job(self, url, job_id=None):
        """Load job page and all async content

        Params:
            - url {str}: url of the profile to be loaded
        Raises:
            ValueError: if link doesn't match a typical profile url
        """

        if job_id:
            url = 'http://www.linkedin.com/jobs/view/' + job_id
        if 'com/jobs/view' not in url:
            raise ValueError("Url must look like ...linkedin.com/jobs/view/JOB")
        self.current_job = url.split(r'com/jobs/view/')[1]
        self.driver.get(url)

        # Wait for page to load dynamically via javascript
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.ID, 'careers'))))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load job. Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor""")

    def load_detailed_info(self):
        more_button = self.driver.find_element_by_css_selector('.view-more-icon')
        more_button.click()
        WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.jobs-description-details__list-item')
        ))

    def scrape_by_page(self, keywords='', location='', n=2):
        # Need to enforce proper format for keywords and location somehow...
        self.load_index(keywords,location)
        self.page_num = 1

        output = []
        for i in range(n):
            output.append(self.scrape_page())
            self.next_page()
        return output

    def load_index(self,keywords='',location=''):
        url = 'http://www.linkedin.com/jobs/search/?keywords={}&location={}&sortBy==DD'.format(keywords,location)
        self.driver.get(url)

        # Wait for page to load dynamically via javascript
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.jobs-search-results')),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.not-found-404'))
            ))
        except TimeoutException as e:
            raise Exception(
                """Took too long to load search results. Common problems/solution:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow internet: increase the timeout parameter in the Scraper constructor""")

        # Scroll to load lazy-loaded content
        self.scroll_sidebar()

    def scrape_page(self):
        search_results = self.driver.find_elements(By.CSS_SELECTOR,
            '.job-card-search--clickable')
        
        output = []
        for job in search_results:
            job.click()
            output.append(self.scrape_sub_window())

        return output

    def scrape_sub_window(self):
        basics_html = self.driver.find_element_by_css_selector(
            '.jobs-details-top-card').get_attribute('outerHTML')
        details_html = self.driver.find_element_by_css_selector(
            '.jobs-description__container').get_attribute('outerHTML')
        job_id = self.driver.find_element_by_css_selector(
            '.jobs-details-top-card__job-title-link').get_attribute('href').split('/')[2]

        return Job(job_id,basics_html,details_html)

    def next_page(self):
        page_list = self.driver.find_elements(By.CSS_SELECTOR,'button.data-ember-action')
        print(len(page_list))
        for page in page_list:
            if page.get_attribute('text') == str(self.page_num):
                page.click()
                break

        self.wait(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, 'li.active'), str(self.page_num + 1)
        ))
        self.page_num += 1
        self.scroll_sidebar()

    def scroll_sidebar(self):
        sidebar = self.driver.find_element(By.CSS_SELECTOR,'.jobs-search-results') 
        sidebar.send_keys(Keys.PAGE_DOWN)
