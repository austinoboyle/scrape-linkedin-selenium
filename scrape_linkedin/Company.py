from .utils import *
from .ResultsObject import ResultsObject
from bs4 import BeautifulSoup
import re


class Company(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['overview', 'jobs', 'life']

    def __init__(self, overview, jobs="", life=""):
        self.overview_soup = BeautifulSoup(overview, 'html.parser')
        self.jobs_soup = BeautifulSoup(overview, 'html.parser')
        self.life_soup = BeautifulSoup(overview, 'html.parser')

    @property
    def overview(self):
        """Return dict of the overview section of the Linkedin Page"""

        # Banner containing company Name + Location
        banner = one_or_default(
            self.overview_soup, '.org-top-card')

        # Main container with company overview info
        container = one_or_default(
            self.overview_soup, '.org-grid__core-rail')

        overview = {}
        overview['description'] = container.select_one(
            'section > p').get_text().strip()

        metadata_keys = container.select('.org-page-details__definition-term')
        metadata_values = container.select(
            '.org-page-details__definition-text')
        overview.update(
            get_info(banner, {'name': '.org-top-card-primary-content__title'}))

        for key, val in zip(metadata_keys, metadata_values):
            dict_key = key.get_text().strip().lower().replace(" ", "_")
            dict_val = val.get_text().strip()
            overview[dict_key] = dict_val

        all_employees_links = all_or_default(
            banner, '.org-company-employees-snackbar__details-highlight')

        if all_employees_links:
            all_employees_text = all_employees_links[-1].text
        else:
            all_employees_text = ''

        match = re.search(r'((\d+?,?)+)', all_employees_text)
        if match:
            overview['num_employees'] = int(match.group(1).replace(',', ''))
        else:
            overview['num_employees'] = None
        return overview

    @property
    def jobs(self):
        return None

    @property
    def life(self):
        return None
