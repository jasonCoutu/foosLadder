from google.appengine.ext import ndb

from app.models import PlayerModel

def get_entities(query=None):
    """ Get all PlayerModels by a query, or get all of them """
    if query:
        return PlayerModel.query(query)
    else:
        return PlayerModel.query()


def get_by_email(query):
    if query:
        return PlayerModel.query(PlayerModel.key == get_key(query)).get()
    else:
        return None


def get_key(query):
    if query:
        return ndb.Key(PlayerModel, query)
    else:
        return None


def update_player_name(first_name, last_name, key):
    if not key:
        raise ValueError("Key is required to update player")
    if not first_name:
        raise ValueError("First name is required")
    if not last_name:
        raise ValueError("Last name is required")

    player = get_by_email(key)
    player.first_name = first_name
    player.last_name = last_name
    return player.put()


def new_player(email, first_name, last_name, skillScore, skillBase):
    if not email:
        raise ValueError("Email is required")
    if not first_name:
        raise ValueError("First name is required")
    if not last_name:
        raise ValueError("Last name is required")
    if not skillScore:
        raise ValueError("SkillScore is required")
    if not skillBase:
        raise ValueError("SkillBase is required")

    player = PlayerModel(key=PlayerModel.build_key(email))
    player.first_name = first_name
    player.last_name = last_name
    player.skillScore = skillScore
    player.skillBase = skillBase

    return player.put()

# How it used to work:
# a = PlayerModel(key=keys[0])
# a.skillBase = self.request.POST['skillBaseVal']
# a.first_name = fname
# a.last_name = lname
# a.gamesPlayed = played
# a.gamesWon = won
# a.skillScore = int(skillBase_names[a.skillBase])
# logging.debug("Putting new Player %s" % key)
# a.put()