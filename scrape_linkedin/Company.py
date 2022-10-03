import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

from .ResultsObject import ResultsObject
from .utils import all_or_default, get_info, one_or_default, text_or_default

RE_DUPLICATE_WHITESPACE = re.compile(r"[\s]{2,}")
COMPANY_SIZE_KEY = 'company_size'

logger = logging.getLogger(__name__)


def get_company_metadata(about_section):
    """
    Takes a Company's 'About' section, and returns a dict mapping metadata keys
    to metadata values. Keys can be somewhat arbitrary, but common ones include
    Company size, industry, website, specialties, headquarters, etc.

    Note that this section container 'titles' and 'values' all at the same level
    of nesting. It looks something like:
     <dl>
       <dt>Heading 1</dt>
       <dd>Some value for heading 1</dd>
       <dd>Another value for heading1</dd>
       <dt>Heading 2</dt>
       ...
     </dl>
    """
    curr_header = None
    results = {}
    for child in all_or_default(about_section, "dl > *"):
        # We've hit a new heading.
        if child.name == 'dt':
            curr_header = child.get_text().lower().strip().replace(" ", "_")
            results[curr_header] = []
        # We've hit content for the most recent heading.
        elif child.name == 'dd':
            content = child.get_text().strip()
            results[curr_header].append(
                RE_DUPLICATE_WHITESPACE.sub(" ", content))  # strip redundant whitespace

    for r in results:
        results[r] = '\n'.join(results[r])
    return results


def get_employee_count(s: str) -> Optional[int]:
    """Extracts employee count from a string."""
    employee_count_match = re.search(r'([\d,]+) on LinkedIn', s)
    if employee_count_match:
        return int(employee_count_match.group(1).replace(",", ""))
    return None


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

        overview = {
            "description": None,
            "image": None,
            "name": None,
            "num_employees": None,
            "metadata": None
        }

        # Banner containing company Name + Location
        banner = one_or_default(
            self.overview_soup, '.org-top-card')

        # Main container with company overview info
        container = one_or_default(self.overview_soup,
                                   '.org-grid__content-height-enforcer')

        overview["name"] = text_or_default(self.overview_soup, "#main h1")
        overview['description'] = text_or_default(container, 'section > p')

        logo_image_tag = one_or_default(
            banner, '.org-top-card-primary-content__logo')
        overview['image'] = logo_image_tag['src'] if logo_image_tag else ''

        company_metadata = get_company_metadata(container)
        overview["metadata"] = company_metadata
        overview["num_employees"] = get_employee_count(company_metadata.get(
            COMPANY_SIZE_KEY, ""))

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
