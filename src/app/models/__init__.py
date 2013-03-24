from google.appengine.ext import ndb

# Old rankings: 'pro':1200,'semi-pro':900, 'elite':700, 'advanced':500, 'adept':400, 'novice':200,'beginner':100
# New rankings: # http://en.wikipedia.org/wiki/Elo_rating_system#United_States_Chess_Federation_ratings
skillBase_names = {"Senior Master": 2400,
                   "National Master": 2200,
                   "Expert": 2000,
                   "Class A": 1800,
                   "Class B": 1600,
                   "Class C": 1400,
                   "Class D": 1200,
                   "Class E": 1000,
                   "Class F": 800,
                   "Class G": 600,
                   "Class H": 400,
                   "Class I": 200,
                   "Class J": 100}


class PlayerModel(ndb.Model):
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)
    gamesPlayed = ndb.IntegerProperty(default=0)
    gamesWon = ndb.IntegerProperty(default=0)
    skillScore = ndb.IntegerProperty(default=100)
    skillBase = ndb.StringProperty(choices=skillBase_names.keys())
    lastGame = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def build_key(cls, email):
        return ndb.Key(PlayerModel, email)


class GameModel(ndb.Model):
    player1 = ndb.IntegerProperty(required=True)
    player2 = ndb.IntegerProperty(required=True)


class MatchModel(ndb.Model):
    gameDate = ndb.DateTimeProperty(auto_now=True)
    player1 = ndb.StringProperty(required=True)
    player2 = ndb.StringProperty(required=True)
    scores = ndb.StructuredProperty(GameModel,repeated=True)
    baseValue = ndb.IntegerProperty(required=True)
