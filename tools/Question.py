__author__ = "Georgios-Ioannis Brokos"
__copyright__ = "Copyright (c) 2016, " + __author__
__license__ = "3-clause BSD"
__email__ = "g.brokos@gmail.com"

class Question(object):
    body = ""
    id = ""
    retrieved = ""
    distances = []

    def __init__(self, body, id, retrieved=[], distances=[]):
        self.body = body
        self.id = id
        self.retrieved = retrieved
        self.distances = distances