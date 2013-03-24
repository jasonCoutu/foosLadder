import logging

from operator import itemgetter

from app.domain import player as player_dom
from app.domain import match as match_dom
from app.utils import calculate_winner, number_to_word


def update_player_name(fname, lname, key):
    player_dom.update_player_name(fname, lname, key)


def compare_players(user, opponent):
    pass


def get_most_games(calc_type="total", top=5):
    """
    Gets the top X number of people with the chosen type of game
    @param calc_type: Which type of games to calculate. The default is "total",
    which will just get all games. Accepted inputs: "wins" and "losses"
    @param top: Number of people to collect
    """
    players = player_dom.get_entities()
    player_games = []
    for player in players:
        email = player.key.id()
        games = 0
        new_player = {
            "email": email,
            "data": 0,
            "full_name": get_player_full_name(email)
        }
        if calc_type == "wins":
            games = player.gamesWon
        elif calc_type == "losses":
            games = player.gamesPlayed - player.gamesWon
        elif calc_type == "total":
            games = player.gamesPlayed
        new_player['data'] = games
        player_games.append(new_player)

    sorted_players = sorted(player_games, key=itemgetter('data'))

    if len(sorted_players) < top:
        top = len(sorted_players)

    return sorted_players[len(sorted_players) - top:]


def get_highest_goals(against=False, top=5):
    """
    Pass in a boolean to tell the method to calculate goals against instead of
    the default which is goals for.
    @return: a list of dictionaries containing the top however many people with
    the highest goals
    @param against: Pass True if you want this to count goals against
    @param top: Pass in the number of "top" people you want (e.g. Top 5)
    """
    players = player_dom.get_entities()

    player_goals = []
    for player in players:
        email = player.key.id()
        matches = match_dom.get_matches_by_email(email)
        goals = 0
        new_player = {
            'email': email,
            'data': 0,
            'full_name': get_player_full_name(email)
        }
        for match in matches:
            if against:
                if match.player1 == email:
                    goals += match.scores[0].player2
                    goals += match.scores[1].player2
                    goals += match.scores[2].player2
                elif match.player2 == email:
                    goals += match.scores[0].player1
                    goals += match.scores[1].player1
                    goals += match.scores[2].player1
            elif not against:
                if match.player1 == email:
                    goals += match.scores[0].player1
                    goals += match.scores[1].player1
                    goals += match.scores[2].player1
                elif match.player2 == email:
                    goals += match.scores[0].player2
                    goals += match.scores[1].player2
                    goals += match.scores[2].player2
        new_player["data"] += goals
        player_goals.append(new_player)

    sorted_players = sorted(player_goals, key=itemgetter('data'))

    if len(sorted_players) < top:
        top = len(sorted_players)

    return sorted_players[len(sorted_players)-top:]


def get_player_full_name(email):
    """
    Returns full name like "first last"
    @param email: Email/key of the person who's name you want
    """
    user = player_dom.get_by_email(email)
    return user.first_name + " " + user.last_name


def calc_player_info(player, key):
    """ Returns information for the player viewing page """
    name = player.first_name
    last = player.last_name
    skill = player.skillScore
    total_wins = player.gamesWon
    games = player.gamesPlayed
    total_losses = games - total_wins
    email = key.pairs()[0][1]
    match_results = match_dom.get_matches_by_email(email, True, 5)

    last_five_wins = 0
    last_five_losses = 0

    for result in match_results:
        wins = 0
        losses = 0
        for i in range(0, len(result.scores)):
            winner = calculate_winner(result.scores[i].player1,
                                      result.scores[i].player2)
            if winner == "player1":
                if result.player1 == email:
                    wins += 1
                elif result.player2 == email:
                    losses += 1
            elif winner == "player2":
                if result.player1 == email:
                    losses += 1
                elif result.player2 == email:
                    wins += 1
        if wins > losses:
            last_five_wins += 1
        elif losses > wins:
            last_five_losses += 1

    total_games = number_to_word(last_five_wins + last_five_losses)

    last_five_games = {"wins": last_five_wins,
                       "losses": last_five_losses,
                       "total": total_games}

    try:
        win_ratio = round(((total_wins / (games * 1.0)) * 100), 2)
    except ZeroDivisionError:
        win_ratio = 0

    match_results = match_dom.get_matches_by_email(email, True)

    streak_wins = 0
    streak_losses = 0
    first = True
    last_result = "wins"
    final_result = ""
    for result in match_results:
        wins = 0
        losses = 0
        if first:
            for i in range(0, len(result.scores)):
                winner = calculate_winner(result.scores[i].player1,
                                          result.scores[i].player2)
                if winner == "player1":
                    if result.player1 == email:
                        wins += 1
                    elif result.player2 == email:
                        losses += 1
                elif winner == "player2":
                    if result.player1 == email:
                        losses += 1
                    elif result.player2 == email:
                        wins += 1
            if wins > losses:
                last_result = "wins"
                streak_wins += 1
            elif losses > wins:
                last_result = "losses"
                streak_losses += 1
            first = False
        else:
            for i in range(0, len(result.scores)):
                winner = calculate_winner(result.scores[i].player1,
                                          result.scores[i].player2)
                if winner == "player1":
                    if result.player1 == email:
                        wins += 1
                    elif result.player2 == email:
                        losses += 1
                elif winner == "player2":
                    if result.player1 == email:
                        losses += 1
                    elif result.player2 == email:
                        wins += 1
            if wins > losses:
                if last_result == "wins":
                    streak_wins += 1
                else:
                    final_result = "Currently on a {} game losing streak".\
                        format(number_to_word(streak_losses))
                    break
            elif losses > wins:
                if last_result == "losses":
                    streak_losses += 1
                else:
                    final_result = "Currently on a {} game winning streak".\
                        format(number_to_word(streak_wins))
                    break
    else:
        if len(match_results) == 0:
            final_result = "Hasn't played any games yet!"

    if final_result == "":
        #Need to calculate it
        if last_result == "wins":
            final_result = "Currently on a {} game winning streak".\
                format(number_to_word(streak_wins))
        elif last_result == "losses":
            final_result = "Currently on a {} game losing streak".\
                format(number_to_word(streak_losses))

    player = {
        "email": email,
        "name": name,
        "last": last,
        "skill": skill,
        "wins": total_wins,
        "losses": total_losses,
        "games": games,
        "win_ratio": win_ratio,
        "last_five_games": last_five_games,
        "streak": final_result
    }

    return player


def match_history(email):
    """

    """
    match_results = match_dom.get_matches_by_email(email, True)

    history = []

    count = 0

    for result in match_results:
        count += 1
        wins = 0
        losses = 0
        for i in range(0, len(result.scores)):
            winner = calculate_winner(result.scores[i].player1,
                                      result.scores[i].player2)
            if winner == "player1":
                if result.player1 == email:
                    wins += 1
                elif result.player2 == email:
                    losses += 1
            elif winner == "player2":
                if result.player1 == email:
                    losses += 1
                elif result.player2 == email:
                    wins += 1

        if result.player1 == email:
            scores = str(result.scores[0].player1) + "-" + \
                str(result.scores[0].player2) + ", " + \
                str(result.scores[1].player1) + "-" + \
                str(result.scores[1].player2) + ", " + \
                str(result.scores[2].player1) + "-" + \
                str(result.scores[2].player2)
        else:
            scores = str(result.scores[0].player2) + "-" + \
                str(result.scores[0].player1) + ", " + \
                str(result.scores[1].player2) + "-" + \
                str(result.scores[1].player1) + ", " + \
                str(result.scores[2].player2) + "-" + \
                str(result.scores[2].player1)

        if wins > losses:

            history.append([count, str(
                result.gameDate.strftime('%b %d, %Y @ %I:%S')),
                True, scores, get_player_full_name(result.player1),
                get_player_full_name(result.player2)])
        elif losses > wins:
            history.append([count, str(
                result.gameDate.strftime('%b %d, %Y @ %I:%S')),
                False, scores, get_player_full_name(result.player1),
                get_player_full_name(result.player2)])

    return history
