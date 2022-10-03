import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .Company import Company
from .Scraper import Scraper
from .utils import AnyEC

logger = logging.getLogger(__name__)


class CompanyScraper(Scraper):
    def scrape(self, company, overview=True, jobs=False, life=False, insights=False):
        self.url = 'https://www.linkedin.com/company/{}'.format(company)
        self.company = company

        self.load_initial()

        jobs_html = life_html = insights_html = overview_html = ''

        if overview:
            overview_html = self.fetch_page_html('about')
        if life:
            life_html = self.fetch_page_html('life')
        if jobs:
            jobs_html = self.fetch_page_html('jobs')
        if insights:
            insights_html = self.fetch_page_html('insights')
        return Company(overview_html, jobs_html, life_html, insights_html)

    def fetch_page_html(self, page):
        """
        Navigates to a company subpage and returns the entire HTML contents of the page.
        """
        try:
            self.driver.get(f"{self.url}/{page}")
            return self.driver.find_element_by_css_selector(
                '.organization-outlet').get_attribute('outerHTML')
        except Exception as e:
            logger.warn(
                f"Unable to fetch '{page}' page for {self.company}: {e}")
            return ''

    def load_initial(self):
        self.driver.get(self.url)
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.organization-outlet')),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.error-container'))
            ))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load company.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor""")
        try:
            self.driver.find_element_by_css_selector('.organization-outlet')
        except:
            raise ValueError(
                'Company Unavailable: Company link does not match any companies on LinkedIn')
