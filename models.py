from google.appengine.ext import ndb

skillBase_names = {'pro':1200,'semi-pro':900, 'elite':700, 'advanced':500, 'adpet':400, 'novice':200,'begginer':100}


class PlayerModel(ndb.Model):
    
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)
    gamesPlayed = ndb.IntegerProperty(default=0)
    gamesWon = ndb.IntegerProperty(default=0)
    skillScore = ndb.IntegerProperty(default=0)
    skillBase =ndb.StringProperty(choices=skillBase_names.keys())
    lastGame = ndb.DateTimeProperty(auto_now=True)


class GameModel(ndb.Model):
    player1 = ndb.IntegerProperty(required=True)
    player2 = ndb.IntegerProperty(required=True)

class MatchModel(ndb.Model):

    gameDate = ndb.DateTimeProperty(auto_now=True)
    player1 = ndb.StringProperty(required=True)
    player2 = ndb.StringProperty(required=True)
    scores = ndb.StructuredProperty(GameModel,repeated=True)
