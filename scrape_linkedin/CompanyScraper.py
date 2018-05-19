from .Scraper import Scraper
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import time
from .Company import Company
from .utils import AnyEC


class CompanyScraper(Scraper):
    def scrape(self, url='', company=None):
        # Get Overview
        self.load_initial(url, company)
        overview_html = self.driver.find_element_by_css_selector(
            '.organization-outlet').get_attribute('outerHTML')

        # Get job Info
        self.load_jobs()
        jobs_html = self.driver.find_element_by_css_selector(
            '.org-jobs-container').get_attribute('outerHTML')

        # Get Life Info
        self.load_life()
        life_html = self.driver.find_element_by_css_selector(
            '.org-life').get_attribute('outerHTML')
        return Company(overview_html, jobs_html, life_html)

    def load_initial(self, url, company=None):
        if company:
            url = 'https://www.linkedin.com/company/{}/'.format(company)
        if 'com/company/' not in url:
            raise ValueError("Url must look like ...linkedin.com/company/NAME")

        self.driver.get(url)
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

    def load_jobs(self):
        jobs_tab = self.driver.find_element_by_css_selector('.nav-jobs-tab')
        jobs_link = jobs_tab.find_element_by_xpath('..')
        jobs_link.click()
        el = WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.org-jobs-container')
        ))

    def load_life(self):
        life_tab = self.driver.find_element_by_css_selector('.nav-lifeat-tab')
        life_link = life_tab.find_element_by_xpath('..')
        life_link.click()
        el = WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.org-life')
        ))
