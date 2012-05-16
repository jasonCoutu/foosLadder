import os
from webapp2 import WSGIApplication, Route

ROUTES = [
    Route('/', handler='views.mainView'),
    Route('/page2', handler='views.playerView'),
    Route('/newPlayer', handler='views.newPlayerView'),
    Route('/selector', handler='views.selectorView'),
    Route('/ladder', handler='views.ladderView'),
    Route('/recordGame', handler='views.reportView'),
    Route('/reportGame', handler='views.reportView'),

    ]

ROUTES2 = [
    Route('/viewAll', handler='views.ladderView'),

    ]



TEMPLATE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')

CONFIG = {'webapp2_extras.jinja2': {'template_path': TEMPLATE_DIR}}

app = WSGIApplication(ROUTES, config=CONFIG)

app2 = WSGIApplication(ROUTES2, config=CONFIG)
