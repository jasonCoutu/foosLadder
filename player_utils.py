import logging

from google.appengine.ext import ndb

from models import PlayerModel

def update_player_name(key, fname, lname):
    keys = ndb.Key(PlayerModel, key )
    user = keys.get()

    user.first_name = fname
    user.last_name = lname

    user.put()

def compare_players(user, opponent):
    pass

def calc_player_info(player):
    """ Returns information for the player viewing page """
    name = player.first_name
    last = player.last_name
    skill = player.skillScore
    wins = player.gamesWon
    games = player.gamesPlayed
    losses = games - wins
    try:
        win_ratio = round(((wins / (games * 1.0)) * 100), 2)
    except ZeroDivisionError:
        win_ratio = 0
    return name, last, skill, wins, losses, games, win_ratio