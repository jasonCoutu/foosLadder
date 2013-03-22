from google.appengine.ext import ndb

from app.models import PlayerModel

def get_entities(query=None):
    """ Get all PlayerModels by a query, or get all of them """
    if query:
        return PlayerModel.query(query)
    else:
        return PlayerModel.query()


def get_by_key(query):
    key = get_key(query)
    if key:
        return key.get()
    else:
        return None


def get_key(query):
    if query:
        return ndb.Key(PlayerModel, query)
    else:
        return None


def update_player(**kwargs):
    player = get_by_key(kwargs["key"])
    if player:
        if "first_name" in kwargs.keys():
            player.first_name = kwargs["first_name"]
        if "last_name" in kwargs.keys():
            player.last_name = kwargs["last_name"]
        return player.put()
    else:
        return None
        # first_name = ndb.StringProperty(required=True)
        # last_name = ndb.StringProperty(required=True)
        # gamesPlayed = ndb.IntegerProperty(default=0)
        # gamesWon = ndb.IntegerProperty(default=0)
        # skillScore = ndb.IntegerProperty(default=100)
        # skillBase =ndb.StringProperty(choices=skillBase_names.keys())
        # lastGame = ndb.DateTimeProperty(auto_now=True)


def new_player(**kwargs):
    player = PlayerModel()
    if "first_name" in kwargs.keys():
        player.first_name = kwargs["first_name"]
    if "last_name" in kwargs.keys():
        player.last_name = kwargs["last_name"]
    if "skillScore" in kwargs.keys():
        player.skillScore = kwargs["skillScore"]
    if "skillBase" in kwargs.keys():
        player.skillBase = kwargs["skillBase"]
    return player.put()
