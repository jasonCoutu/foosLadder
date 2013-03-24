from google.appengine.ext import ndb

from app.models import MatchModel


def get_entities(query=None, order=None):
    """ Get all PlayerModels by a query, or get all of them """
    if query:
        if order:
            return MatchModel.query(query)
        return MatchModel.query(query)
    else:
        return MatchModel.query()


def get_matches_by_email(email, sort=None, limit=None):
    if not email:
        raise ValueError("Must pass an email to check")
    results = MatchModel.query(ndb.OR(MatchModel.player1 == email,
                                      MatchModel.player2 == email))
    if sort:
        results = results.order(-MatchModel.gameDate)
    if limit:
        results = results.fetch(limit)
    return results


def submit_game(match):
    if not match:
        raise ValueError("Must pass in a match to submit")
    if isinstance(match, MatchModel):
        match.put()
    else:
        raise ValueError("Match passed in must be a MatchModel")


def new_match():
    return MatchModel()
