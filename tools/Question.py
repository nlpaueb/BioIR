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