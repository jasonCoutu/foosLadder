__author__ = 'VendAsta'

import logging

from google.appengine.api import users, mail

import app.utils as utils

from app.views import TemplatedView
from app.domain import player as player_dom
from app.domain import match


class ladderView(TemplatedView):

    def post(self):
        game_played = match.new_match()
        game_played.player1 = self.request.POST['player1']
        game_played.player2 = self.request.POST['player2']

        game_played.scores = utils.calculate_score_from_post(self.request)

        #TODO: Break rest of the score calculation into utils.py
        players = player_dom.get_multi_players(players=[game_played.player1,
                                                        game_played.player2])
        p1_total = [game_played.scores[0].player1,
                    game_played.scores[1].player1,
                    game_played.scores[2].player1]
        p2_total = [game_played.scores[0].player2,
                    game_played.scores[1].player2,
                    game_played.scores[2].player2]

        logging.info("Match between %s %s and %s %s" % (players[0].first_name,
                                                        players[0].last_name,
                                                        players[1].first_name,
                                                        players[1].last_name))

        p1_wins = 0
        p2_wins = 0

        for i in range(0, len(p1_total)):
            logging.info("Game %d: %d - %d" % (i + 1, p1_total[i], p2_total[i]))
            if p1_total[i] > p2_total[i]:
                p1_wins += 1
                logging.info("%s wins Game %d" % (players[0].first_name, i + 1))
            elif p2_total[i] > p1_total[i]:
                p2_wins += 1
                logging.info("%s wins Game %d" % (players[1].first_name, i + 1))

        logging.info("%s won %d games; %s won %d games" %
                     (players[0].first_name, p1_wins,
                      players[1].first_name, p2_wins))

        if p1_wins > p2_wins:
            winner = players[0]
            loser = players[1]
        elif p2_wins > p1_wins:
            winner = players[1]
            loser = players[0]
        else:
            logging.info("No score submitted, loading ladder")
            self.redirect("/ladder-redirect")
            return

        logging.info("Winner: %s" % winner)
        logging.info("Loser: %s" % loser)

        logging.info("%s %s's old rank was %d" %
                     (winner.first_name, winner.last_name, winner.skillScore))
        logging.info("%s %s's old rank was %d" %
                     (loser.first_name, loser.last_name, loser.skillScore))

        winnerRank, loserRank = utils.calculate_elo_rank(winner.skillScore,
                                                         loser.skillScore)

        # Try returning the point change for some interesting data
        point_change = int(winnerRank - winner.skillScore)

        logging.info("%s %s's rank is now %d, a change of %d points" %
                     (winner.first_name, winner.last_name, winnerRank,
                      winnerRank - winner.skillScore))
        logging.info("%s %s's rank is now %d, a change of %d points" %
                     (loser.first_name, loser.last_name, loserRank,
                      loser.skillScore - loserRank))

        winner.skillScore = int(winnerRank)
        loser.skillScore = int(loserRank)

        basePoints = int((loser.skillScore - winner.skillScore) * 0.3)
#        #print basePoints
        if basePoints < -100:
            basePoints = 5
        elif basePoints < -20:
            basePoints = 10  # todo: This is wrong, but better.
        elif basePoints < 20:
            basePoints = 20

        game_played.baseValue = basePoints
        match.submit_game(game_played)

#       Not needed with ELO calculations from utils.py
#        bonusPoints = int((basePoints*point_dff)/10)

#        winner.skillScore = winner.skillScore + basePoints + bonusPoints
#        loser.skillScore = loser.skillScore - basePoints - bonusPoints
        winner.gamesWon += 1
        winner.gamesPlayed += 1
        loser.gamesPlayed += 1

        winner.put()
        loser.put()

        user = users.get_current_user()
        user_email = str(user.email())
        if user_email != str(game_played.player1):
            opponent_email = str(game_played.player1)
        else:
            opponent_email = str(game_played.player2)

        #TODO: Break email dispatch into utils.py
        message = mail.EmailMessage()
        message.sender = user_email
        message.to = opponent_email
        message.subject = "Match Entry - VendAsta Foosball Ladder"
        if winner == players[0]:
            message.html = """
<p>A match was entered between %s (winner) and %s (loser).</p>
<p>The game scores were %d-%d, %d-%d, %d-%d</p>
<p>Check out the ladder by going <a href='http://vendladder.appspot.com'>here</a>.</p>
""" % (winner.first_name + " " + winner.last_name,
       loser.first_name + " " + loser.last_name,
       game_played.scores[0].player1, game_played.scores[0].player2,
       game_played.scores[1].player1, game_played.scores[1].player2,
       game_played.scores[2].player1, game_played.scores[2].player2)
        else:
            message.html = """
<p>A match was entered between %s (winner) and %s (loser).</p>
<p>The game scores were %d-%d, %d-%d, %d-%d</p>
<p>Check out the ladder by going <a href='http://vendladder.appspot.com'>here</a>.</p>
""" % (winner.first_name + " " + winner.last_name,
       loser.first_name + " " + loser.last_name,
       game_played.scores[0].player2, game_played.scores[0].player1,
       game_played.scores[1].player2, game_played.scores[1].player1,
       game_played.scores[2].player2, game_played.scores[2].player1)

        logging.info("Emailing %s from %s" % (user_email, opponent_email))

        message.send()

        # self.get(success=True, point_change=point_change)
        self.redirect("/ladder-redirect")

    def get(self, **kwargs):
        players_total, actives = utils.get_ladder()
        user = users.get_current_user()
        players = list()
        for player in players_total.iter():
            if player_dom.has_been_active(1, player):
                players.append((player.key.id(), "%s %s" % (player.first_name,
                                                            player.last_name),
                                player.skillScore))
        self.render_response('ladder.html',
                             players=players,
                             numplayers=players_total.count(),
                             active=actives.count(),
                             user=user,
                             success=kwargs.get("success"),
                             point_change=kwargs.get("point_change"))
