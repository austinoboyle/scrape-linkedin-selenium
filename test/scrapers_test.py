from scrape_linkedin import CompanyScraper, ProfileScraper, HEADLESS_OPTIONS
from selenium.webdriver import Chrome
import os


def test_profile_scraper():
    with ProfileScraper(driver_options=HEADLESS_OPTIONS) as ps:
        profile = ps.scrape(user='austinoboyle')

    profile_info = profile.to_dict()

    for a in profile.attributes:
        assert profile_info[a]

    # Skills
    skills = profile_info['skills']
    for s in skills:
        assert s['name'] is not None
        assert len(s['endorsements']) > 0

    # Personal Info
    personal_info = profile_info['personal_info']
    assert personal_info['name'] == "Austin O'Boyle"
    assert len(personal_info['websites']) > 0
    non_nulls = ['headline', 'company', 'school',
                 'summary', 'location', 'followers', 'email', 'image']
    for a in non_nulls:
        assert personal_info[a]

    # Accomplishments
    accomplishments = profile_info['accomplishments']
    non_nulls = ['certifications', 'courses',
                 'honors', 'projects', 'languages']
    for a in non_nulls:
        assert accomplishments[a]

    # Interests
    assert profile_info['interests']

    # Experiences
    experiences = profile_info['experiences']
    jobs = experiences['jobs']
    assert jobs
    for job in jobs:
        assert job['date_range']
        assert job['company']
        assert job['title']

    education = experiences['education']
    assert education
    for school in education:
        assert school['name']
        assert school['date_range']

    volunteering = experiences['volunteering']
    assert volunteering
    for v in volunteering:
        assert v['title']
        assert v['date_range']


def test_company_scraper():
    with CompanyScraper(driver_options=HEADLESS_OPTIONS) as cs:
        company = cs.scrape(company='facebook')

    company_info = company.to_dict()

    overview = company.overview
    assert overview
    overview_fields = ['specialties', 'founded', 'website', 'description', 'name',
                       'num_employees', 'industry', 'type', 'company_size', 'headquarters']
    for a in overview_fields:
        assert overview[a]
