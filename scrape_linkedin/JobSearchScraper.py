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

    def scrape(self,keywords='',location=''):
        # Need to enforce proper format for keywords and location somehow...
        self.load_index(keywords,location)
        self.page_num = 1
        return self.scrape_page()

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

    def scrape_page(self):
        search_results = self.driver.find_elements(By.CSS_SELECTOR, '.job-card-search__link-wrapper')
        # Remove duplicate elements
        search_results = list(set(search_results))

        output = []
        with JobScraper(cookie=str(os.getenv('LI_AT'))) as scraper:
            for job in search_results:
                output.append(scraper.scrape(url=job.get_attribute('href')))

        return output
