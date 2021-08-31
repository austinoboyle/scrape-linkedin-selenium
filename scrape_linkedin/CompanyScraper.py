import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .Company import Company
from .Scraper import Scraper
from .utils import AnyEC

import time

logger = logging.getLogger(__name__)


class CompanyScraper(Scraper):
    def scrape(self, company, overview=True, jobs=True, life=False, insights=False, people=True):
        # Get Overview
        self.load_initial(company)
        self.company = company

        jobs_html = life_html = insights_html = overview_html = people_html = ''

        if overview:
            overview_html = self.get_overview()
        if life:
            life_html = self.get_life()
        if insights:
            insights_html = self.get_insights()
        if people:
            people_html = self.get_people()
        if jobs:
            jobs_html = self.get_jobs()

        #print("JOBS", jobs_html, "\n\n\n\n\nLIFE", life_html)
        return Company(overview_html, jobs_html, life_html, insights_html, people_html)

    def load_initial(self, company):
        url = 'https://www.linkedin.com/company/{}'.format(company)

        self.driver.get(url)
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.organization-outlet')),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.error-container'))
            ))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load company.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor""")
        try:
            self.driver.find_element_by_css_selector('.organization-outlet')
        except:
            raise ValueError(
                'Company Unavailable: Company link does not match any companies on LinkedIn')
    
    def click_on_tab(self, tab_name):
        main_url = "https://www.linkedin.com/company/{}/".format(self.company)
        try:
            self.driver.get(main_url + tab_name)
        except:
            print("Tab cannot be found.")
            return

    
    def get_overview(self):
        try:
            self.click_on_tab('about')
            self.wait_for_el(
                'section.artdeco-card.p4.mb3')
            return self.driver.find_element_by_css_selector(
                'div.scaffold-layout__row.scaffold-layout__content').get_attribute('outerHTML')
        except:
            return ''

    def get_life(self):
        try:
            self.click_on_tab('life')
            self.wait_for_el(
                'a[data-control-name="page_member_main_nav_life_tab"].active')
            return self.driver.find_element_by_css_selector('.org-life').get_attribute('outerHTML')
        except:
            return ''

    def get_jobs(self):
        try:
            self.click_on_tab('jobs')
            self.wait_for_el(
                'a.link-without-hover-visited.mt5.ember-view')
            self.driver.execute_script(
                "document.getElementsByClassName('link-without-hover-visited mt5 ember-view')[0].click()")
            time.sleep(5)
            job_html = ''
            
            def click_on_job():
                html = ''
                containers = self.driver.find_elements_by_css_selector(
                    'li.jobs-search-results__list-item.occludable-update.p0.relative')
                for container in containers:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView(true);", container)
                    container.find_element_by_css_selector(
                        'div.job-card-container.relative').click()
                    time.sleep(1)
                    self.wait_for_el(
                        'div.jobs-unified-top-card__job-insight')
                    html += self.driver.find_element_by_css_selector(
                        'div.jobs-unified-top-card__content--two-pane').get_attribute('outerHTML')
                return html

            buttons = self.driver.find_elements_by_css_selector(
                'li.artdeco-pagination__indicator.artdeco-pagination__indicator--number')
            if buttons:
                last_button = int(buttons[-1].get_attribute('data-test-pagination-page-btn'))
                for page in range(1, last_button + 1):
                    job_html += click_on_job()
                    buttons = self.driver.find_elements_by_css_selector(
                        'li.artdeco-pagination__indicator.artdeco-pagination__indicator--number > button')
                    for next_page in buttons:
                        if int(next_page.get_attribute('aria-label').split()[1]) == page + 1:
                            next_page.click()
                            time.sleep(2)
                            break
            else:
                job_html += click_on_job()

            # with open('output.html', 'w', encoding = "utf-8") as output:
            #     output.write(str(job_html))
            return job_html
        except:
            return ''

    def get_insights(self):
        try:
            self.click_on_tab('home')
            self.wait_for_el(
                'a[data-control-name="page_member_main_nav_insights_tab"].active')
            return self.driver.find_element_by_css_selector(
                '.org-premium-insights-module').get_attribute('outerHTML')
        except:
            return ''

    def get_people(self):
        try:
            self.click_on_tab('people')
            self.wait_for_el(
                'div.artdeco-card.pv5.pl5.pr1.mt4')
            stats = self.driver.find_elements_by_css_selector(
                '.artdeco-carousel__item-container')
            stats_container = ''
            for index in range(0, len(stats), 2):
                stats_container += stats[index].get_attribute('outerHTML')
                if index == len(stats)-1:
                    break
                stats_container += stats[index+1].get_attribute('outerHTML')
                self.driver.find_element_by_css_selector(
                    'button.artdeco-pagination__button.artdeco-pagination__button--next').click()
                time.sleep(1)
            
            for _ in range(100):
                height = self.driver.execute_script('return document.body.scrollHeight')
                scroll = 'window.scrollTo(0, ' + str(height) + ');'
                self.driver.execute_script(scroll)
                time.sleep(1)
                scroll_2 = 'window.scrollTo(0, ' + str(height-100) + ');'
                self.driver.execute_script(scroll_2)
                time.sleep(1)
            people_container = self.driver.find_element_by_css_selector(
                '.artdeco-card.pv5.pl5.pr1.mt4').get_attribute('outerHTML')
            
            # with open('new_out.html','w',encoding = "utf-8") as out:
            #     out.write(str(stats_container + people_container))
            return stats_container + people_container
        except:
            return ''