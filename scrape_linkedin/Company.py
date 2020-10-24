from .utils import *
from .ResultsObject import ResultsObject
from bs4 import BeautifulSoup
import re


class Company(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['overview', 'jobs', 'life', 'insights']
    # KD adds insights attribute

    def __init__(self, overview, jobs, life, insights):
        # KD fixed attributes making jobs and life undefined as they are defined in CompanyScraper, and this allows insights to work
        self.overview_soup = BeautifulSoup(overview, 'html.parser')
        self.jobs_soup = BeautifulSoup(jobs, 'html.parser')
        self.life_soup = BeautifulSoup(life, 'html.parser')
        self.insights_soup = BeautifulSoup(insights, 'html.parser')
        # KD adds insights soup

    @property
    def overview(self):
        """Return dict of the overview section of the Linkedin Page"""

        # Banner containing company Name + Location
        banner = one_or_default(
            self.overview_soup, '.org-top-card')

        # Main container with company overview info
        container = one_or_default(
            self.overview_soup, '.org-grid__core-rail--wide')

        overview = {}
        overview['description'] = container.select_one(
            'section > p').get_text().strip()

        metadata_keys = container.select('.org-page-details__definition-term')
        print(metadata_keys)
        metadata_keys = [x for x in metadata_keys if "Company size" not in x.get_text()]
        print(metadata_keys)
        metadata_values = container.select(
            '.org-page-details__definition-text')
        overview.update(
            get_info(banner, {'name': '.org-top-card-summary__title'})) # A fix to the name selector
        overview.update(
            get_info(container, {'company_size': '.org-about-company-module__company-size-definition-text'})) # Manually added Company size

        for key, val in zip(metadata_keys, metadata_values):
            dict_key = key.get_text().strip().lower().replace(" ", "_")
            dict_val = val.get_text().strip()
            if "company_size" not in dict_key:
                overview[dict_key] = dict_val
        print(overview)

        all_employees_links = all_or_default(
            banner, '.mt2 > a > span') # A fix to locate "See all ### employees on LinkedIn"

        if all_employees_links:
            all_employees_text = all_employees_links[-1].text
        else:
            all_employees_text = ''

        match = re.search(r'((\d+?,?)+)', all_employees_text)
        if match:
            overview['num_employees'] = int(match.group(1).replace(',', ''))
        else:
            overview['num_employees'] = None

        logo_image_tag = one_or_default(
            banner, '.org-top-card-primary-content__logo')
        overview['image'] = logo_image_tag['src'] if logo_image_tag else ''

        return overview

    @property
    def jobs(self):
        return None

    @property
    def life(self):
        return None

    # KD added property for Insights
    @property
    def insights(self):

        # summary table containing the Insights data for % change in headcount at 6m, 1y and 2y
        table = one_or_default(
            self.insights_soup, '.org-insights-module__summary-table')

        insights = {}

        insights.update(get_info(table, {
            '6m change': 'td:nth-of-type(2) span:nth-of-type(3)',
            '1y change': 'td:nth-of-type(3) span:nth-of-type(3)',
            '2y change': 'td:nth-of-type(4) span:nth-of-type(3)'

        }))
        return insights
