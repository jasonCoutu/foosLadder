__author__ = 'VendAsta'

from google.appengine.ext import ndb

import utils
import logging

from views import TemplatedView
from models import PlayerModel, GameModel, MatchModel, skillBase_names

class ladderView(TemplatedView):

    def post(self):
        """
            formula for scoring:
                Winner's skill  (ws)
                Loser's skill   (ls)
                Base points     (bp)
                Bonus Points    (pb)
                Point Diff      (pd)

                wp - lp = bp
                if bp <20 : bp = 20
                pb = bp*pd/10
                ws = ws + bp + pb
                ls = ls - bp - pb
        """

        a = MatchModel()
        a.player1 = self.request.POST['player1']
        a.player2 = self.request.POST['player2']
        a.scores = utils.calculate_score_from_post(self.request)
        players = ndb.get_multi([ndb.Key(PlayerModel, a.player1), ndb.Key(PlayerModel, a.player2)])
        p1_total = a.scores[0].player1 + a.scores[1].player1 + a.scores[2].player1
        p2_total = a.scores[0].player2 + a.scores[1].player2 + a.scores[2].player2

    #        point_dff =  p1_total - p2_total
            #print point_dff

        if p1_total > p2_total:
            winner = players[0]
            loser = players[1]
        elif p2_total > p1_total:
            winner = players[1]
            loser = players[0]
#            point_dff = point_dff * -1
        else:
            #No winner or loser, don't adjust the rankings at all
            self.get()
            return


        winnerRank, loserRank  = utils.calculate_elo_rank(winner.skillScore,
                                                          loser.skillScore)

        winner.skillScore = int(winnerRank)
        loser.skillScore = int(loserRank)

        basePoints = int((loser.skillScore - winner.skillScore) * 0.3)
#        #print basePoints
        if basePoints < -100 :
            basePoints = 5
        elif basePoints < -20:
            basePoints = 10 #todo: This is wrong, but better.
        elif basePoints < 20:
            basePoints = 20

        a.baseValue = basePoints
        a.put()

#       Not needed with ELO calculations from utils.py
#        bonusPoints = int((basePoints*point_dff)/10)

#        winner.skillScore = winner.skillScore + basePoints + bonusPoints
#        loser.skillScore = loser.skillScore - basePoints - bonusPoints
        winner.gamesWon += 1
        winner.gamesPlayed += 1
        loser.gamesPlayed += 1
        winner.put()
        loser.put()

        self.get()


    def get(self):
        players_total, actives = utils.get_ladder()
        self.render_response('ladder.html',
            players=[i for i in players_total.iter()],
            numplayers=players_total.count(), active=actives.count())

