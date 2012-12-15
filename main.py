import os
from webapp2 import WSGIApplication, Route, SimpleRoute

ROUTES = [
    Route('/',              handler='views.mainView'),
    Route('/player',        handler='views.playerView'),
    Route('/newPlayer',     handler='views.newPlayerView'),
    Route('/selector',      handler='views.selectorView'),
    Route('/ladder',        handler='ladder.ladderView'),
    Route('/recordGame',    handler='views.reportView'),
    Route('/reportGame',    handler='views.reportView'),
    Route('/settings',      handler='views.settingsView'),
    Route('/compare',       handler='views.compareView'),
    Route('/playerView',    handler='views.playerStatsView'),
    Route('/about',         handler='views.aboutView'),
    Route('/leaderboard',   handler='views.leaderboardView'),
    SimpleRoute('/.+',      handler='views.errorHandler'),
    ]

ROUTES2 = [
    Route('/viewAll', handler='views.ladderView'),
    ]

TEMPLATE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')

CONFIG = {'webapp2_extras.jinja2': {'template_path': TEMPLATE_DIR}}

app = WSGIApplication(ROUTES, config=CONFIG)

app2 = WSGIApplication(ROUTES2, config=CONFIG)
