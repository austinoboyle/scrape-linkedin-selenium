from .Scraper import Scraper
import re
import time

MY_CONNECTIONS_LINK = 'https://www.linkedin.com/mynetwork/invite-connect/connections/'


class MyConnectionScraper(Scraper):
    def scrape(self):
        self.driver.get(MY_CONNECTIONS_LINK)
        self.wait_for_el('.mn-connection-card')
        total_connections_text = self.driver.find_element_by_css_selector(
            '.mn-connections > h2').text
        self.total_connections = int(re.search(
            r'(\d+)', total_connections_text).group(1))
        self.scroll_to_bottom()
        return self.get_all_connections()

    def get_all_connections(self):
        connections = []
        for el in self.visible_connections:
            connection = {}
            connection['name'] = el.find_element_by_css_selector(
                '.mn-connection-card__name').text
            connection['connected_time'] = el.find_element_by_css_selector(
                'time').text
            connection_link = el.find_element_by_css_selector(
                '.mn-connection-card__link').get_attribute('href')
            connection['id'] = re.search(
                r'/in/(.*?)/', connection_link).group(1)
            connections.append(connection)
        return connections

    def scroll_to_bottom(self):
        num_visible_connections = 0
        consecutive_same_num = 1
        MAX_CONSECUTIVE = 20
        while num_visible_connections < self.total_connections and consecutive_same_num < MAX_CONSECUTIVE:
            prev_visible_connections = num_visible_connections
            num_visible_connections = len(self.visible_connections)
            if (prev_visible_connections == num_visible_connections):
                consecutive_same_num += 1
            else:
                consecutive_same_num = 1
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(self.scroll_pause)

    @property
    def visible_connections(self):
        return self.driver.find_elements_by_css_selector('.mn-connection-card')
