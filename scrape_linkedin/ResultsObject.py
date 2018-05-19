from bs4 import BeautifulSoup


class ResultsObject(object):
    attributes = []

    def __init__(self, body):
        self.soup = BeautifulSoup(body, 'html.parser')

    def to_dict(self):
        keys = self.attributes
        vals = map(lambda attr: getattr(self, attr), self.attributes)
        return dict(zip(self.attributes, vals))

    def __dict__(self):
        return self.to_dict()

    def __eq__(self, that):
        return that.__dict__() == self.__dict__()
