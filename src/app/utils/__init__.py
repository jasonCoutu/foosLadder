import math

from app.domain import game as game_dom
from app.domain import player as player_dom

PLAYER_A = 1
PLAYER_B = 2


#TODO: use this http://elo.divergentinformatics.com/ (or something like it)
def calculate_elo_rank(player_a_rank=1600, player_b_rank=1600, winner=PLAYER_A,
                       penalize_loser=True):
    if winner is PLAYER_A:
        winner_rank, loser_rank = player_a_rank, player_b_rank
    else:
        winner_rank, loser_rank = player_b_rank, player_a_rank
    rank_diff = winner_rank - loser_rank
    exp = (rank_diff * -1) / 400
    odds = 1 / (1 + math.pow(10, exp))
    if winner_rank < 2100:
        k = 32
    elif 2100 >= winner_rank < 2400:
        k = 24
    else:
        k = 16
        # Triple the points baby (doesn't really work)
    k *= 3
    new_winner_rank = round(winner_rank + (k * (1 - odds)))
    if penalize_loser:
        # Triple the points baby (doesn't really work)
        new_rank_diff = new_winner_rank - winner_rank
        new_loser_rank = loser_rank - new_rank_diff
    else:
        new_loser_rank = loser_rank
    if new_loser_rank < 1:
        new_loser_rank = 1
    if new_loser_rank < 100:
        new_loser_rank = 100
    if winner is PLAYER_A:
        return new_winner_rank, new_loser_rank
    return new_loser_rank, new_winner_rank


def get_ladder():
    players = player_dom.get_players_sorted_skill_score(False)
    active_players = player_dom.get_active_players(1)

    return players, active_players


def calculate_score_from_post(request):
    game1 = game_dom.new_game()
    game2 = game_dom.new_game()
    game3 = game_dom.new_game()
    if "game1" in request.POST.keys():
        winners = [request.POST['game1'],
                   request.POST['game2'],
                   request.POST['game3']]
        if winners[0] == "player1":
            game1.player1 = 5
            game1.player2 = 0
        else:
            game1.player2 = 5
            game1.player1 = 0
        if winners[1] == "player1":
            game2.player1 = 5
            game2.player2 = 0
        else:
            game2.player2 = 5
            game2.player1 = 0
        if winners[2] == "player1":
            game3.player1 = 5
            game3.player2 = 0
        else:
            game3.player2 = 5
            game3.player1 = 0
    else:
        game1.player1 = int(request.POST['p1g1'])
        game1.player2 = int(request.POST['p2g1'])

        game2.player1 = int(request.POST['p1g2'])
        game2.player2 = int(request.POST['p2g2'])

        game3.player1 = int(request.POST['p1g3'])
        game3.player2 = int(request.POST['p2g3'])

    return [game1, game2, game3]


def calculate_winner(p1_score, p2_score):
    if p1_score > p2_score:
        return "player1"
    elif p2_score > p1_score:
        return "player2"
    else:
        return "tied"


def number_to_word(number):
    if number > 9 or number < 0:
        return number
    else:
        if number == 0:
            return "zero"
        elif number == 1:
            return "one"
        elif number == 2:
            return "two"
        elif number == 3:
            return "three"
        elif number == 4:
            return "four"
        elif number == 5:
            return "five"
        elif number == 6:
            return "six"
        elif number == 7:
            return "seven"
        elif number == 8:
            return "eight"
        elif number == 9:
            return "nine"