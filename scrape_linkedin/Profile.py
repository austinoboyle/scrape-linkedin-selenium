from bs4 import BeautifulSoup
from pprint import pprint
from .utils import *


class Profile(object):
    """Linkedin Profile object

    Attributes:
        - personal_info
        - experiences
        - skills
        - accomplishments
        - interests
        - to_dict: return dictionary of all properties listed above
    """
    attributes = ['personal_info', 'experiences',
                  'skills', 'accomplishments', 'interests']

    def __init__(self, body):
        """Initializes a profile with beautifulsoup body"""
        self.soup = BeautifulSoup(body, 'html.parser')

    @property
    def personal_info(self):
        """Return dict of personal info about the user"""
        info = {}
        top_card = one_or_default(self.soup, 'section.pv-top-card-section')

        personal_info = get_info(top_card, {
            'name': '.pv-top-card-section__name',
            'headline': '.pv-top-card-section__headline',
            'company': '.pv-top-card-v2-section__company-name',
            'school': '.pv-top-card-v2-section__school-name',
            'location': '.pv-top-card-section__location',
            'summary': 'p.pv-top-card-section__summary-text'
        })
        followers_text = text_or_default(self.soup,
                                         '.pv-recent-activity-section__follower-count-text')
        personal_info['followers'] = followers_text.replace(
            'followers', '').strip()
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

        jobs = all_or_default(container, '#experience-section ul > li')
        jobs = list(map(get_job_info, jobs))
        experiences['jobs'] = jobs

        schools = all_or_default(container, '#education-section ul > li')
        schools = list(map(get_school_info, schools))
        experiences['education'] = schools

        volunteering = all_or_default(
            container, '.pv-profile-section.volunteering-section ul > li')
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
        """Return full dict of person's profile
        """
        info = {}
        info['personal_info'] = self.personal_info
        info['experiences'] = self.experiences
        info['skills'] = self.skills
        info['accomplishments'] = self.accomplishments
        info['interests'] = self.interests
        return info

    def __dict__(self):
        return self.to_dict()

    def __eq__(self, that):
        return self.to_dict() == that.to_dict()


if __name__ == '__main__':
    with open('test.html', 'r') as inFile:
        profile = Profile(inFile.read())
        pprint(profile.to_dict())
