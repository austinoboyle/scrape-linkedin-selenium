from .utils import *
from .ResultsObject import ResultsObject
import re


class Profile(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['personal_info', 'experiences',
                  'skills', 'accomplishments', 'interests']

    @property
    def personal_info(self):
        """Return dict of personal info about the user"""
        top_card = one_or_default(self.soup, 'section.pv-top-card-section')
        contact_info = one_or_default(self.soup, '.pv-contact-info')

        personal_info = get_info(top_card, {
            'name': '.pv-top-card-section__name',
            'headline': '.pv-top-card-section__headline',
            'company': '.pv-top-card-v2-section__company-name',
            'school': '.pv-top-card-v2-section__school-name',
            'location': '.pv-top-card-section__location',
            'summary': 'p.pv-top-card-section__summary-text'
        })

        image_div = one_or_default(top_card, '.profile-photo-edit__preview')
        image_url = ''
        # print(image_div)
        if image_div:
            image_url = image_div['src']
        else:
            image_div = one_or_default(top_card, '.pv-top-card-section__photo')
            style_string = image_div['style']
            pattern = re.compile('background-image: url\("(.*?)"')
            matches = pattern.match(style_string).groups()
            if matches:
                image_url = matches[0]

        personal_info['image'] = image_url

        followers_text = text_or_default(self.soup,
                                         '.pv-recent-activity-section__follower-count', '')
        personal_info['followers'] = followers_text.replace(
            'followers', '').strip()

        # print(contact_info)
        personal_info.update(get_info(contact_info, {
            'email': '.ci-email .pv-contact-info__ci-container',
            'phone': '.ci-phone .pv-contact-info__ci-container',
            'connected': '.ci-connected .pv-contact-info__ci-container'
        }))

        websites = contact_info.select('.ci-websites li a')
        websites = list(map(lambda x: x['href'], websites))
        personal_info['websites'] = websites
        return personal_info

    @property
    def experiences(self):
        """
        Returns:
            dict of person's professional experiences.  These include:
                - Jobs
                - Education
                - Volunteer Experiences
        """
        experiences = {}
        container = one_or_default(self.soup, '.background-section')

        jobs = all_or_default(
            container, '#experience-section ul .pv-position-entity')
        jobs = list(map(get_job_info, jobs))
        jobs = flatten_list(jobs)

        experiences['jobs'] = jobs

        schools = all_or_default(
            container, '#education-section .pv-education-entity')
        schools = list(map(get_school_info, schools))
        experiences['education'] = schools

        volunteering = all_or_default(
            container, '.pv-profile-section.volunteering-section .pv-volunteering-entity')
        volunteering = list(map(get_volunteer_info, volunteering))
        experiences['volunteering'] = volunteering

        return experiences

    @property
    def skills(self):
        """
        Returns:
            list of skills {name: str, endorsements: int} in decreasing order of
            endorsement quantity.
        """
        skills = self.soup.select('.pv-skill-category-entity__skill-wrapper')
        skills = list(map(get_skill_info, skills))

        # Sort skills based on endorsements.  If the person has no endorsements
        def sort_skills(x): return int(
            x['endorsements'].replace('+', '')) if x['endorsements'] else 0
        return sorted(skills, key=sort_skills, reverse=True)

    @property
    def accomplishments(self):
        """
        Returns:
            dict of professional accomplishments including:
                - publications
                - cerfifications
                - patents
                - courses
                - projects
                - honors
                - test scores
                - languages
                - organizations
        """
        accomplishments = dict.fromkeys([
            'publications', 'certifications', 'patents',
            'courses', 'projects', 'honors',
            'test_scores', 'languages', 'organizations'
        ])
        container = one_or_default(self.soup, '.pv-accomplishments-section')
        for key in accomplishments:
            accs = all_or_default(container, 'section.' + key + ' ul > li')
            accs = map(lambda acc: acc.get_text() if acc else None, accs)
            accomplishments[key] = list(accs)
        return accomplishments

    @property
    def interests(self):
        """
        Returns:
            list of person's interests
        """
        container = one_or_default(self.soup, '.pv-interests-section')
        interests = all_or_default(container, 'ul > li')
        interests = map(lambda i: text_or_default(
            i, '.pv-entity__summary-title'), interests)
        return list(interests)

    def to_dict(self):
        info = super(Profile, self).to_dict()
        info['personal_info']['current_company_link'] = ''
        jobs = info['experiences']['jobs']
        if jobs and 'present' in jobs[0]['date_range'].lower():
            info['personal_info']['current_company_link'] = jobs[0]['li_company_url']
        return info
