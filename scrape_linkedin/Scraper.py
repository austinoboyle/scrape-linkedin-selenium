import json
import selenium.webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import time
from .Profile import Profile
from .utils import AnyEC
from os import environ


class Scraper(object):
    """
    Wrapper for selenium Chrome driver with methods to scroll through a page and
    to scrape and parse info from a linkedin profile

    Params:
        - cookie {str}: li_at session cookie required to scrape linkedin profiles
        - driver {webdriver}: driver to be used for scraping
        - scroll_pause {float}: amount of time to pause (s) while incrementally
        scrolling through the page
        - scroll_increment {int}: pixel increment for scrolling
        - timeout {float}: time to wait for page to load first batch of async content
    """

    def __init__(self, cookie=None, driver=selenium.webdriver.Chrome, scroll_pause=0.1, scroll_increment=300, timeout=10):
        if not cookie:
            if 'LI_AT' not in environ:
                raise ValueError(
                    'Must either define LI_AT environment variable, or pass a cookie string to the Scraper')
            cookie = environ['LI_AT']
        self.driver = driver()
        self.scroll_pause = scroll_pause
        self.scroll_increment = scroll_increment
        self.timeout = timeout
        self.driver.get('http://www.linkedin.com')
        self.driver.set_window_size(1200, 1000)
        self.driver.add_cookie({
            'name': 'li_at',
            'value': cookie,
            'domain': '.linkedin.com'
        })

    def load_profile_page(self, url, user=None):
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
            raise ValueError(
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
        # Scroll to the bottom of the page incrementally to load any lazy-loaded content
        self.scroll_to_bottom()

    def get_profile(self, url):
        self.load_profile_page(url)
        profile = self.driver.find_element_by_id(
            'profile-wrapper').get_attribute("outerHTML")
        return Profile(profile)

    def get_html(self, url):
        self.load_profile_page(url)
        return self.driver.page_source

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page

        Params:
            - scroll_pause_time {float}: time to wait (s) between page scroll increments
            - scroll_increment {int}: increment size of page scrolls (pixels)
        """
        expandable_button_selectors = [
            'button[aria-expanded="false"].pv-skills-section__additional-skills',
            'button[aria-expanded="false"].pv-profile-section__see-more-inline',
            'button[aria-expanded="false"].pv-top-card-section__summary-toggle-button',
            'button[data-control-name="contact_see_more"]'
        ]

        current_height = 0
        while True:
            for name in expandable_button_selectors:
                try:
                    self.driver.find_element_by_css_selector(name).click()
                except:
                    pass
            # Scroll down to bottom
            new_height = self.driver.execute_script(
                "return Math.min({}, document.body.scrollHeight)".format(current_height + self.scroll_increment))
            if (new_height == current_height):
                break
            self.driver.execute_script(
                "window.scrollTo(0, Math.min({}, document.body.scrollHeight));".format(new_height))
            current_height = new_height
            # Wait to load page
            time.sleep(self.scroll_pause)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.quit()

    def quit(self):
        if self.driver:
            self.driver.quit()
