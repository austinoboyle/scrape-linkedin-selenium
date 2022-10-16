import logging
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .Company import Company
from .Scraper import Scraper
from .utils import AnyEC

logger = logging.getLogger(__name__)


class CompanyScraper(Scraper):

    def scrape(self,
               company,
               org_type="company",
               overview=True,
               jobs=False,
               life=False,
               insights=False,
               people=False):

        # org_type = "company" or "school"
        # This will allow to switch between school and company urls
        # The underlying functionality is same for both scrapers
        # Added parameters - org_type, people
        # people page for company is same as alumni for org_type="school"
        # people page for company shows employees data whereas for school it shows alumni data

        self.url = 'https://www.linkedin.com/{org_type}/{company}'.format(
            org_type=org_type, company=company)
        self.company = company

        self.load_initial()

        people_html = jobs_html = life_html = insights_html = overview_html = ''

        if overview:
            overview_html = self.fetch_page_html('about')
        if life:
            life_html = self.fetch_page_html('life')
        if jobs:
            jobs_html = self.fetch_page_html('jobs')
        if insights:
            insights_html = self.fetch_page_html('insights')
        if people:
            people_html = self.fetch_page_html('people')

        return Company(overview_html, jobs_html, life_html, insights_html,
                       people_html)

    def fetch_page_html(self, page):
        """
        Navigates to a company subpage and returns the entire HTML contents of the page.
        """

        if page == "people":
            interval = 2.0
        else:
            interval = 0.1

        try:
            self.driver.get(f"{self.url}/{page}")
            # people/alumni javascript takes more time to load
            time.sleep(interval)

            return self.driver.find_element_by_css_selector(
                '.organization-outlet').get_attribute('outerHTML')
        except Exception as e:
            logger.warn(
                f"Unable to fetch '{page}' page for {self.company}: {e}")
            return ''

    def load_initial(self):
        self.driver.get(self.url)
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(
                AnyEC(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '.organization-outlet')),
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '.error-container'))))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load company.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor"""
            )
        try:
            self.driver.find_element_by_css_selector('.organization-outlet')
        except:
            raise ValueError(
                'Company Unavailable: Company link does not match any companies on LinkedIn'
            )
