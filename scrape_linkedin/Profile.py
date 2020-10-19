from .utils import *
from .ResultsObject import ResultsObject
import re
from datetime import datetime


class Profile(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['personal_info', 'experiences',
                  'skills', 'accomplishments', 'interests']

    @property
    def personal_info(self):
        """Return dict of personal info about the user"""
        top_card = one_or_default(self.soup, '.pv-top-card')
        contact_info = one_or_default(self.soup, '.pv-contact-info')

        # Note that some of these selectors may have multiple selections, but
        # get_info takes the first match
        personal_info = get_info(top_card, {
            'name': '.pv-top-card--list > li',
            'headline': '.flex-1.mr5 h2',
            'company': 'li[data-control-name="position_see_more"]',
            'school': 'li[data-control-name="education_see_more"]',
            'location': '.pv-top-card--list-bullet > li',
        })

        personal_info['summary'] = text_or_default(
            self.soup, '.pv-about-section .pv-about__summary-text', '').replace('... see more', '').strip()

        image_url = ''
        # If this is not None, you were scraping your own profile.
        image_element = one_or_default(
            top_card, 'img.profile-photo-edit__preview')

        if not image_element:
            image_element = one_or_default(
                top_card, 'img.pv-top-card-section__photo')

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

    @property
    def recommendations(self):
        recs = {
            'received': [],
            'given': [],
        }
        rec_block = one_or_default(self.soup, '.recommendations-inlining')
        if rec_block:
            div_blocks = rec_block.find_all('div', recursive=False)
            if div_blocks:
                rec_tabs = div_blocks[-1]
                if rec_tabs:
                    buttons_and_rec_blocks = rec_tabs.find_all('div', recursive=False)
                    if buttons_and_rec_blocks:
                        buttons = all_or_default(buttons_and_rec_blocks[0], 'button')
                        if buttons:
                            expr = re.compile(r'((?<=in\/).+(?=\/)|(?<=in\/).+)')  # re to get li id
                            date_expr = re.compile(r'\w+ \d{2}, \d{4}, ')  # re to get date of recommendation
                            for idx, b in enumerate(buttons):
                                for rec_type in recs.keys():
                                    if rec_type in str(b.contents).lower():
                                        recs_category = buttons_and_rec_blocks[idx + 1]  # +1 --> skip buttons block
                                        for rec in recs_category.find_all('li', {'class': 'pv-recommendation-entity'}):
                                            rec_dict = {
                                                'text': None,
                                                'date': None,
                                                'relationship': None,
                                                'recommender': {
                                                    'firstName': None,
                                                    'lastName': None,
                                                    'occupation': None,
                                                    'li_id': None
                                                }
                                            }
                                            text_spans = rec.find_all('span',
                                                                      {
                                                                          'class': ['lt-line-clamp__line',
                                                                                    'lt-line-clamp__raw-line']
                                                                      })
                                            rec_text_list = [span.text for span in text_spans]
                                            rec_text_list = [t.replace('\n', '').replace('  ', '').replace('\r', '') for t in rec_text_list]
                                            rec_dict['text'] = ''.join(rec_text_list)

                                            recommender = one_or_default(rec, '.pv-recommendation-entity__member')
                                            if recommender:
                                                try:
                                                    rec_dict['recommender']['li_id'] = expr.search(
                                                        recommender.attrs['href']).group()
                                                except AttributeError as e:
                                                    pass

                                                recommender_detail = one_or_default(recommender, '.pv-recommendation-entity__detail')
                                                if recommender_detail:
                                                    name = text_or_default(recommender, 'h3')
                                                    name = name.replace('\n', '')
                                                    name = name.replace('  ', '')
                                                    name = name.replace('\r', '')
                                                    name_splitted = name.split(' ', maxsplit=1)
                                                    rec_dict['recommender']['firstName'] = name_splitted[0]
                                                    rec_dict['recommender']['lastName'] = name_splitted[1]

                                                    recommender_ps = recommender_detail.find_all('p', recursive=False)
                                                    if len(recommender_ps) == 2:
                                                        recommender_headline, recommender_meta = recommender_detail.find_all(
                                                            'p')
                                                        if recommender_headline:
                                                            headline = text_or_default(recommender, 'h3')
                                                            headline = headline.replace('\n', '')
                                                            headline = headline.replace('  ', '')
                                                            headline = headline.replace('\r', '')
                                                            rec_dict['recommender']['occupation'] = headline

                                                        if recommender_meta:
                                                            try:
                                                                match = date_expr.search(recommender_meta.text).group()
                                                                dt = datetime.strptime(match, '%B %d, %Y, ')
                                                                rec_dict['date'] = dt.strftime('%Y-%m-%d')
                                                                relationship = recommender_meta.text.split(match)[-1]
                                                                relationship = relationship.replace('\n', '')
                                                                relationship = relationship.replace('  ', '')
                                                                relationship = relationship.replace('\r', '')
                                                                rec_dict['relationship'] = relationship
                                                            except (ValueError, AttributeError) as e:
                                                                pass

                                            recs[rec_type].append(rec_dict)
        return recs

    def to_dict(self):
        info = super(Profile, self).to_dict()
        info['personal_info']['current_company_link'] = ''
        jobs = info['experiences']['jobs']
        if jobs and jobs[0]['date_range'] and 'present' in jobs[0]['date_range'].lower():
            info['personal_info']['current_company_link'] = jobs[0]['li_company_url']
        else:
            print("Unable to determine current company...continuing")
        return info
