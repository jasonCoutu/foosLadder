from app.models import MatchModel


def get_entities(query=None, order=None):
    """ Get all PlayerModels by a query, or get all of them """
    if query:
        if order:
            return MatchModel.query(query)
        return MatchModel.query(query)
    else:
        return MatchModel.query()


def submit_game(match):
    if not match:
        raise ValueError("Must pass in a match to submit")
    if isinstance(match, MatchModel):
        match.put()
    else:
        raise ValueError("Match passed in must be a MatchModel")


def new_match():
    return MatchModel()
