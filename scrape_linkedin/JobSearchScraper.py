from .Scraper import Scraper
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from .JobScraper import JobScraper
import time
from .utils import AnyEC
from bs4 import BeautifulSoup
import os

class JobSearchScraper(Scraper):
    """
    Scraper for collecting job information by location or keyword. See inherited Scraper class for details.
    """

    def scrape(self, keywords='',location=''):
        # Need to enforce proper format for keywords and location somehow...
        self.load_index(keywords,location)
        self.page_num = 1
        return self.scrape_page()

    def scrape_by_page(self, keywords='', location='', num_pages=2):
        self.load_index(keywords,location)
        self.page_num = 1

        output = []
        for i in range(num_pages):
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

        # Make sure we are in the classic view
        self.change_view(view='classic')
        # Scroll to load lazy-loaded content
        self.scroll_to_bottom()

    def scrape_page(self):
        search_results = self.driver.find_elements(By.CSS_SELECTOR,
            '.job-card-search__link-wrapper')
        # Remove duplicate elements
        result_ids = []
        for job in search_results:
            job_id = job.get_attribute('href').split('/')[5]
            if job_id not in result_ids:
                result_ids.append(job_id)

        output = []
        with JobScraper(cookie=str(os.getenv('LI_AT'))) as scraper:
            for job_id in result_ids:
                output.append(scraper.scrape(job_id=job_id))

        return output

    def next_page(self):
        next_btn = self.driver.find_element(By.CSS_SELECTOR, 'button.next')
        next_btn.click()

        self.wait(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, 'li.active'), str(self.page_num + 1)
        ))
        self.page_num += 1
        self.change_view(view='classic')
        self.scroll_to_bottom()

    def change_view(self,view):
        """Change user interface of job search between split and classic modes"""
        available_views = ['split','classic']
        if view not in available_views:
            raise ValueError("View must be one of the following: " + str(available_views)[1:-1])

        self.driver.find_element(By.CSS_SELECTOR,'.jobs-search-dropdown__trigger-icon').click()
        WebDriverWait(self.driver, self.timeout).until(AnyEC(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.jobs-search-dropdown__option'))))

        options = self.driver.find_elements(By.CSS_SELECTOR, 'button.jobs-search-dropdown__option-button')
        for option in options:
            if option.text.lower() == view + ' view':
                option.click()
                break
        WebDriverWait(self.driver, self.timeout).until(AnyEC(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.jobs-search-two-pane__wrapper--single-pane'))))
