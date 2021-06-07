import logging

from .ResultsObject import ResultsObject
from .utils import *

logger = logging.getLogger(__name__)


class Profile(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['personal_info', 'experiences',
                  'skills', 'accomplishments', 'interests', 'recommendations']

    @property
    def personal_info(self):
        """Return dict of personal info about the user"""
        personal_info = dict.fromkeys(['name', 'headline', 'company', 'school', 'location',
                                      'summary', 'image', 'followers', 'email', 'phone', 'connected', 'websites'])
        try:
            top_card = one_or_default(self.soup, '.pv-top-card')
            contact_info = one_or_default(self.soup, '.pv-contact-info')

            # Note that some of these selectors may have multiple selections, but
            # get_info takes the first match
            personal_info = {**personal_info, **get_info(top_card, {
                'name': '.pv-top-card--list > li',
                'headline': '.flex-1.mr5 h2',
                'company': 'li[data-control-name="position_see_more"]',
                'school': 'li[data-control-name="education_see_more"]',
                'location': '.pv-top-card--list-bullet > li',
            })}

            personal_info['summary'] = text_or_default(
                self.soup, '.pv-about-section .pv-about__summary-text', '').replace('... see more', '').strip()

            image_url = ''
            # If this is not None, you were scraping your own profile.
            image_element = one_or_default(
                top_card, 'img.profile-photo-edit__preview')

            if not image_element:
                image_element = one_or_default(
                    top_card, 'img.pv-top-card__photo')

            # Set image url to the src of the image html tag, if it exists
            try:
                image_url = image_element['src']
            except:
                pass

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

            personal_info['websites'] = []
            if contact_info:
                websites = contact_info.select('.ci-websites li a')
                websites = list(map(lambda x: x['href'], websites))
                personal_info['websites'] = websites
        except Exception as e:
            logger.exception(
                "Encountered error while fetching personal_info. Details may be incomplete/missing/wrong: %s", e)
        finally:
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
        experiences = dict.fromkeys(
            ['jobs', 'education', 'volunteering'], [])
        try:
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
        except Exception as e:
            logger.exception(
                "Failed while determining experiences. Results may be missing/incorrect: %s", e)
        finally:
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
        try:
            container = one_or_default(
                self.soup, '.pv-accomplishments-section')
            for key in accomplishments:
                accs = all_or_default(
                    container, 'section.' + key + ' ul > li')
                accs = map(lambda acc: acc.get_text() if acc else None, accs)
                accomplishments[key] = list(accs)
        except Exception as e:
            logger.exception(
                "Failed to get accomplishments, results may be incomplete/missing/wrong: %s", e)
        finally:
            return accomplishments

    @property
    def interests(self):
        """
        Returns:
            list of person's interests
        """
        interests = []
        try:
            container = one_or_default(self.soup, '.pv-interests-section')
            interests = all_or_default(container, 'ul > li')
            interests = list(map(lambda i: text_or_default(
                i, '.pv-entity__summary-title'), interests))
        except Exception as e:
            logger.exception("Failed to get interests: %s", e)
        finally:
            return interests

    @property
    def recommendations(self):
        recs = dict.fromkeys(['received', 'given'], [])
        try:
            rec_block = one_or_default(
                self.soup, 'section.pv-recommendations-section')
            received, given = all_or_default(
                rec_block, 'div.artdeco-tabpanel')
            for rec_received in all_or_default(received, "li.pv-recommendation-entity"):
                recs["received"].append(
                    get_recommendation_details(rec_received))

            for rec_given in all_or_default(given, "li.pv-recommendation-entity"):
                recs["given"].append(get_recommendation_details(rec_given))
        except Exception as e:
            logger.exception("Failed to get recommendations: %s", e)
        finally:
            return recs

    def to_dict(self):
        info = super(Profile, self).to_dict()
        try:
            info['personal_info']['current_company_link'] = ''
            jobs = info['experiences']['jobs']
            if jobs and jobs[0]['date_range'] and 'present' in jobs[0]['date_range'].lower():
                info['personal_info']['current_company_link'] = jobs[0]['li_company_url']
            else:
                raise Exception("Could not determine current company.")
        except Exception as e:
            logger.exception(
                "Could not determine current company's link: %s", e)
        finally:
            return info
