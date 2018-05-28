from .utils import *
from .ResultsObject import ResultsObject
from bs4 import BeautifulSoup

class Job(ResultsObject):
    """LinkedIn Job Object"""

    attributes = ['basic_info', 'detailed_info']

    def __init__(self,job_id,basic_info,detailed_info):
        self.basic_soup = BeautifulSoup(basic_info, 'html.parser')
        self.detailed_soup = BeautifulSoup(detailed_info, 'html.parser')
        self.job_id = job_id

    @property
    def basic_info(self):
        """Return dict of the basic job information from the LinkedIn Page"""
        top_card = one_or_default(
            self.basic_soup, '.jobs-details-top-card__content-container')

        basic_info = get_info(top_card, {
            'title': '.jobs-details-top-card__job-title',
            'job_id': '',
            'location': '.jobs-details-top-card__bullet',
            'company_name': '.jobs-details-top-card__company-info',
            'company_id': '',
            'company_image_link': ''
        })

        # Fill in missing values
        company_img = self.basic_soup.find('img')
        if company_img:
            basic_info['company_image_link'] = company_img['src']

        company_link = self.basic_soup.find('a')
        if company_link:
            basic_info['company_id'] = company_link['href'].split("/")[2]

        basic_info['job_id'] = self.job_id

        # Additional formatting
        basic_info['location'] = basic_info['location'].split('\n')[1].strip()
        basic_info['company_name'] = basic_info['company_name'].split('\n')[1].strip()
        
        return basic_info

    @property
    def detailed_info(self):
        """Return dict of the detailed job information from the LinkedIn page"""
        jobs_box = one_or_default(
            self.detailed_soup, '.jobs-description__content')

        detailed_info = get_info(jobs_box, {
            'job_description': '.jobs-description-content__text',
            'seniority_level': '.js-formatted-exp-body',
            'industries': '.js-formatted-industries-list',
            'employment_type': '.js-formatted-employment-status-body',
            'job_functions': '.js-formatted-job-functions-list'
        })

        # Additional formatting
        if detailed_info['industries']:
            detailed_info['industries'] = detailed_info['industries'].split('\n')
        if detailed_info['job_functions']:
            detailed_info['job_functions'] = detailed_info['job_functions'].split('\n')

        return detailed_info
