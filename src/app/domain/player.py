import datetime

from app.models import PlayerModel


def get_entities(query=None):
    """ Get all PlayerModels by a query, or get all of them """
    if query:
        return PlayerModel.query(query)
    else:
        return PlayerModel.query()


def get_multi_players(**kwargs):
    players = list()

    if "players" in kwargs.keys():
        for player in kwargs["players"]:
            current_player = get_by_email(player)
            if current_player:
                players.append(current_player)
            else:
                raise ValueError("Player must have a key that is their email")

    return players


def get_active_players(days):
    if not days:
        raise ValueError("Must have a value to search for")
    players = get_entities()
    delta = datetime.datetime.now() - datetime.timedelta(days=days)

    return players.filter(PlayerModel.lastGame > delta)


def has_been_active(days, player):
    if not days:
        raise ValueError("Must pass in amount of days to check")
    if not isinstance(player, PlayerModel):
        raise ValueError("You must pass in a PlayerModel")
    delta = datetime.datetime.now() - datetime.timedelta(days=days)
    if player.lastGame > delta:
        return True
    return False


def get_players_sorted_skill_score(asc=True):
    players = get_entities()
    if asc:
        players = players.order(PlayerModel.skillScore)
    else:
        players = players.order(-PlayerModel.skillScore)
    return players


def get_by_email(query):
    if query:
        return PlayerModel.query(PlayerModel.key == get_key(query)).get()
    else:
        return None


def get_key(email):
    """ Build a PlayerModel key from an email passed in
    """
    if email:
        return PlayerModel.build_key(email)
    else:
        return None


def update_player_name(first_name, last_name, key):
    """ Only supports updating the first and last name for now """
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

    player = PlayerModel(key=get_key(email))
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