__author__ = 'VendAsta'

from views import TemplatedView
from models import PlayerModel, GameModel, MatchModel, skillBase_names


class ladderView(TemplatedView):

    def post(self):
        """
            formula for scoreing:
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
        game1 = GameModel()
        game1.player1 = int(self.request.POST['p1g1'])
        game1.player2 = int(self.request.POST['p2g1'])
        game2 = GameModel()
        game2.player1 = int(self.request.POST['p1g2'])
        game2.player2 = int(self.request.POST['p2g2'])
        game3 = GameModel()
        game3.player1 = int(self.request.POST['p1g3'])
        game3.player2 = int(self.request.POST['p2g3'])
        a = MatchModel()
        a.player1 = self.request.POST['player1']
        a.player2 = self.request.POST['player2']
        a.scores = [game1, game2, game3 ]
        players = ndb.get_multi([ndb.Key(PlayerModel, a.player1), ndb.Key(PlayerModel, a.player2)])
        p1_total = game1.player1 + game2.player1 + game3.player1
        p2_total = game1.player2 + game2.player2 + game3.player2

        point_dff =  p1_total - p2_total
        #print point_dff

        if p1_total > p2_total:
            winner = players[0]
            loser = players[1]
        else:
            winner = players[1]
            loser = players[0]
            point_dff = point_dff * -1

        basePoints = int((loser.skillScore - winner.skillScore) * 0.3)
        #print basePoints
        if basePoints < -100 :
            basePoints = 5
        elif basePoints < -20:
            basePoints = 10 #todo: This is wrong, but better.
        elif basePoints < 20:
            basePoints = 20

        a.baseValue = basePoints
        a.put()

        bonusPoints = int((basePoints*point_dff)/10)

        winner.skillScore = winner.skillScore + basePoints + bonusPoints
        loser.skillScore = loser.skillScore - basePoints - bonusPoints
        winner.gamesWon += 1
        winner.gamesPlayed += 1
        loser.gamesPlayed += 1
        winner.put()
        loser.put()

        #print self.request.POST
        self.get()


    def get(self):
        import datetime
        keys = []
        a=PlayerModel.query()
        a=a.order(-PlayerModel.skillScore)
        b=PlayerModel.query()
        lastweek = datetime.datetime.now() - datetime.timedelta(days=7)

        b=b.filter(PlayerModel.lastGame > lastweek)
        self.render_response('ladder.html', players=[i for i in a.iter()] ,numplayers=a.count(), active=b.count())
