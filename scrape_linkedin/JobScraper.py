from .Scraper import Scraper
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import time
from .Job import Job
from .utils import AnyEC


class JobScraper(Scraper):
    """
    Scraper for LinkedIn job postings. See inherited Scraper class for 
    details about the constructor.
    """

    def scrape(self, url='', job_id=None):
        self.load_initial(url, job_id)
        
        # Get basic info
        basics_html = self.driver.find_element_by_css_selector(
                '.jobs-details-top-card').get_attribute('outerHTML')

        # Get detailed info
        #try:
        #    self.load_detailed_info(job_id)
        #    details_html = self.driver.find_element_by_css_selector(
        #        '.jobs-description__container').get_attribute('outerHTML')
        #except:
        #    details_html = ''
        details_html = self.driver.find_element_by_css_selector(
            '.jobs-description__container').get_attribute('outerHTML')
        
        return Job(job_id,basics_html,details_html)

    def load_initial(self, url, job_id=None):
        """Load job page and all async content

        Params:
            - url {str}: url of the profile to be loaded
        Raises:
            ValueError: If link doesn't match a typical profile url"""

        if job_id:
            url = 'http://www.linkedin.com/jobs/view/' + job_id
        if 'com/jobs/view/' not in url:
            raise ValueError("Url must look like ...linkedin.com/jobs/view/JOB")
        self.current_job = url.split(r'com/jobs/view/')[1]
        self.driver.get(url)

        # Wait for page to load dynamically via javascript
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.ID, 'careers')),
        #        EC.presence_of_element_located(
        #            (By.CSS_SELECTOR, '.error-illustration'))
            ))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load job.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor""")

        # Check if we got the error page
        #try:
        #    self.driver.find_element_by_id('error-illustration')
        #except:
        #    raise ValueError(
        #        'Job Unavailable: either this job does not exist or LinkedIn is having problems')

        # Scroll to the bottom of the page incrementally to load any lazy-loaded content
        self.scroll_to_bottom()

    def load_detailed_info(self):
        more_button = self.driver.find_element_by_css_selector('.view-more-icon')
        more_button.click()
        WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR,'.jobs-description-details__list-item')
        ))
