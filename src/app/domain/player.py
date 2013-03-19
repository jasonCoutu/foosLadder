from google.appengine.ext import ndb

from app.models import PlayerModel

    # first_name = ndb.StringProperty(required=True)
    # last_name = ndb.StringProperty(required=True)
    # gamesPlayed = ndb.IntegerProperty(default=0)
    # gamesWon = ndb.IntegerProperty(default=0)
    # skillScore = ndb.IntegerProperty(default=100)
    # skillBase =ndb.StringProperty(choices=skillBase_names.keys())
    # lastGame = ndb.DateTimeProperty(auto_now=True)

def get_entities(query=None):
    """ Get all PlayerModels by a query, or get all of them """
    if query:
        return PlayerModel.query(query)
    else:
        return PlayerModel.query()


def get_by_key(key):
    key = ndb.Key(PlayerModel, key)
    if key:
        return key.get()
    else:
        return None


def new_player(**kwargs):
    pass