from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class ResultsObject(object):
    attributes = []

    def __init__(self, body):
        self.soup = BeautifulSoup(body, 'html.parser')

    def _get_attr_or_none(self, attr):
        try:
            return getattr(self, attr)
        except Exception as e:
            logger.error("Failed to get attribute '%s': %s", attr, e)
            return None

    def to_dict(self):
        keys = self.attributes
        vals = map(self._get_attr_or_none, self.attributes)
        return dict(zip(self.attributes, vals))

    def __dict__(self):
        return self.to_dict()

    def __eq__(self, that):
        return that.__dict__() == self.__dict__()
