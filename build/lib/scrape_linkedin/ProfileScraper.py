import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .ConnectionScraper import ConnectionScraper
from .Profile import Profile
from .Scraper import Scraper
from .utils import AnyEC

logger = logging.getLogger(__name__)


class ProfileScraper(Scraper):
    """
    Scraper for Personal LinkedIn Profiles. See inherited Scraper class for
    details about the constructor.
    """
    MAIN_SELECTOR = '.scaffold-layout__main'
    ERROR_SELECTOR = '.profile-unavailable'

    def scrape_by_email(self, email):
        self.load_profile_page(
            'https://www.linkedin.com/sales/gmail/profile/proxy/{}'.format(email))
        return self.get_profile()

    def scrape(self, url='', user=None):
        self.load_profile_page(url, user)
        return self.get_profile()

    def load_profile_page(self, url='', user=None):
        """Load profile page and all async content

        Params:
            - url {str}: url of the profile to be loaded
        Raises:
            ValueError: If link doesn't match a typical profile url
        """
        if user:
            url = 'https://www.linkedin.com/in/' + user
        if 'com/in/' not in url and 'sales/gmail/profile/proxy/' not in url:
            raise ValueError(
                "Url must look like... .com/in/NAME or... '.com/sales/gmail/profile/proxy/EMAIL")

        logger.debug("Scraping profile for URL %s", url)

        self.driver.get(url)
        # Wait for page to load dynamically via javascript
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.MAIN_SELECTOR)),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.ERROR_SELECTOR))
            ))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load profile.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the time out parameter in the Scraper
                   constructor
                3. Invalid e-mail address (or user does not allow e-mail scrapes) on scrape_by_email call
                """)

        # Check if we got the 'profile unavailable' page
        try:
            self.driver.find_element_by_css_selector(self.MAIN_SELECTOR)
        except:
            raise ValueError(
                'Profile Unavailable: Profile link does not match any current Linkedin Profiles')
        # Scroll to the bottom of the page incrementally to load any lazy-loaded content
        self.scroll_to_bottom()
        self.expand_given_recommendations()

    def expand_given_recommendations(self):
        try:
            given_recommendation_tab = self.driver.find_element_by_css_selector(
                'section.pv-recommendations-section button[aria-selected="false"].artdeco-tab')
            # Scrolls the desired element into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView(false);", given_recommendation_tab)
            given_recommendation_tab.click()
            self.click_expandable_buttons()
            # self.scroll_to_bottom()
        except:
            pass

    def get_profile(self):
        try:
            profile = self.driver.find_element_by_css_selector(
                self.MAIN_SELECTOR).get_attribute("outerHTML")
        except Exception as e:
            logger.exception(
                "Could not find profile wrapper html. This sometimes happens for exceptionally long profiles.  Try decreasing scroll-increment. The actual error was: %s", e)
            raise e
        contact_info = self.get_contact_info()
        return Profile(profile + contact_info)

    def get_contact_info(self):
        try:
            # Scroll to top to put clickable button in view
            self.driver.execute_script("window.scrollTo(0, 0);")
            button = self.driver.find_element_by_partial_link_text(
                'Contact info')
            button.click()
            contact_info = self.wait_for_el('.pv-contact-info')
            return contact_info.get_attribute('outerHTML')
        except Exception as e:
            logger.warning(
                "Failed to open/get contact info HTML. Returning an empty string.", e)
            return ""

    def get_mutual_connections(self):
        try:
            link = self.driver.find_element_by_partial_link_text(
                'Mutual Connection')
        except NoSuchElementException as e:
            logger.warning(
                "Could not find a mutual connections link. Returning an empty list.")
            return []
        with ConnectionScraper(scraperInstance=self) as cs:
            cs.driver.get(link.get_attribute('href'))
            cs.wait_for_el('.search-s-facet--facetNetwork form button')
            return cs.scrape_all_pages()
