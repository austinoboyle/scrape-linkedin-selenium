import logging
import re

from bs4 import BeautifulSoup

from .ResultsObject import ResultsObject
from .utils import AnyEC, all_or_default, get_info, one_or_default

logger = logging.getLogger(__name__)


class Company(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['overview', 'jobs', 'life', 'insights', 'people']
    # KD adds insights attribute

    def __init__(self, overview, jobs, life, insights, people):
        # KD fixed attributes making jobs and life undefined as they are defined in CompanyScraper, and this allows insights to work
        self.overview_soup = BeautifulSoup(overview, 'html.parser')
        self.jobs_soup = BeautifulSoup(jobs, 'html.parser')
        self.life_soup = BeautifulSoup(life, 'html.parser')
        self.insights_soup = BeautifulSoup(insights, 'html.parser')
        self.people_soup = BeautifulSoup(people, 'html.parser')
        # KD adds insights soup

    @property
    def overview(self):
        """Return dict of the overview section of the Linkedin Page"""

        # Banner containing company Name + Location
        banner = one_or_default(
            self.overview_soup, 'section.org-top-card')
        
        # Main container with company overview info
        container = one_or_default(
            self.overview_soup, 'section.artdeco-card.p4.mb3')
        
        overview = {}
        overview['description'] = container.select_one(
            'section > p').get_text().strip()
        
        metadata_keys = container.select('.org-page-details__definition-term')
        # print(metadata_keys)
        metadata_keys = [
            x for x in metadata_keys if "Company size" not in x.get_text()]
        # print(metadata_keys)
        metadata_values = container.select(
            '.org-page-details__definition-text')
        overview.update(
            get_info(banner, {'name': '.t-24.t-black.t-bold'}))  # A fix to the name selector
        overview.update(
            get_info(container, {'company_size': '.org-about-company-module__company-size-definition-text'}))  # Manually added Company size

        for key, val in zip(metadata_keys, metadata_values):
            dict_key = key.get_text().strip().lower().replace(" ", "_")
            dict_val = val.get_text().strip()
            if "company_size" not in dict_key:
                overview[dict_key] = dict_val
        # print(overview)

        all_employees_links = all_or_default(
            banner, '.mt1 > div > a:nth-of-type(2) > span')  # A fix to locate "See all ### employees on LinkedIn"

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
        jobs = {}
        containers = self.jobs_soup.select(
            'div.jobs-unified-top-card__content--two-pane')
        for container in containers:
            role = container.select_one(
                'h2.t-24.t-bold')   
            company = container.select_one(
                'a.ember-view.t-black.t-normal')
            l_r_container = container.select_one(
                'span.jobs-unified-top-card__subtitle-primary-grouping')
            location = l_r_container.select_one(
                'span:nth-of-type(2)')
            remote = l_r_container.select_one(
                'span:nth-of-type(3)')
            posted = container.select_one(
                'span.jobs-unified-top-card__posted-date')
            applicants = container.select_one(
                'span.jobs-unified-top-card__applicant-count')
            job_details = container.select(
                'div.jobs-unified-top-card__job-insight > span')
            
            recruiting, job_type, employees = None, None, None
            if len(job_details) > 1:
                job_type = job_details[0].get_text().strip()
                employees = job_details[1].get_text().strip()
            if len(job_details) > 3:
                recruiting = job_details[3].get_text().strip()
            if company:
                company = company.get_text().strip()
            if location:
                location = location.get_text().strip()
            if remote:
                remote = remote.get_text().strip()
            if posted:
                posted = posted.get_text().strip()
            if applicants:
                applicants = applicants.get_text().strip()
            if role:
                role = role.get_text().strip()
            elif not role:
                continue
            jobs[role] = {"company": company, "location": location,
                "remote": remote, "posted": posted, "applicants": applicants,
                "job_type": job_type, "employees": employees, "recruiting": recruiting}
        return jobs

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
    
    @property
    def people(self):
        people = {
            'Stats': {}, 
            'People_you_may_know': {}
        }
        stats_containers = self.people_soup.select('div.artdeco-carousel__item-container')
        for container in stats_containers:
            heading = container.select_one(
                'div > div > div > h4').get_text().strip()
            people['Stats'].update({heading: []})
            elements = container.select('.org-people-bar-graph-element__percentage-bar-info')
            for element in elements:
                text = element.get_text().strip()
                people['Stats'][heading].append(text)
        
        people_containers = self.people_soup.select('div.org-people-profile-card__profile-info')
        for container in people_containers:
            name = container.select_one(
                'div.org-people-profile-card__profile-title')
            if name:
                name = name.get_text().strip()
                info = container.select_one(
                    'div.lt-line-clamp.lt-line-clamp--multi-line').get_text().strip()
                # image_url = container.select_one('div > div > a > img')['src']
                # image_url = None
                people['People_you_may_know'][name] = info
        return people
