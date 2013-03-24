import os

from webapp2 import WSGIApplication, Route, SimpleRoute

ROUTES = [
    Route('/',              handler='app.views.mainView'),
    Route('/player',        handler='app.views.playerView'),
    Route('/newPlayer',     handler='app.views.newPlayerView'),
    Route('/selector',      handler='app.views.selectorView'),
    Route('/ladder',        handler='app.views.ladder.ladderView'),
    Route('/recordGame',    handler='app.views.reportView'),
    Route('/reportGame',    handler='app.views.reportView'),
    Route('/settings',      handler='app.views.settingsView'),
    Route('/compare',       handler='app.views.compareView'),
    Route('/playerView',    handler='app.views.playerStatsView'),
    Route('/about',         handler='app.views.aboutView'),
    Route('/leaderboard',   handler='app.views.leaderboardView'),
    Route('/matchHistory',  handler='app.views.matchHistoryView'),
    Route('/matchHistoryCalc', handler='app.views.matchHistoryCalc'),
    Route('/ladder-redirect', handler='app.views.ladderRedirect'),
    SimpleRoute('/.+',      handler='app.views.errorHandler'),
]

TEMPLATE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'templates')

CONFIG = {'webapp2_extras.jinja2': {'template_path': TEMPLATE_DIR}}

app = WSGIApplication(ROUTES, config=CONFIG)
