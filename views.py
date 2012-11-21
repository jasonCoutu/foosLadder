import logging

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.webapp._webapp25 import RequestHandler
from webapp2 import RequestHandler, cached_property
from webapp2_extras import jinja2

import utils
import player_utils
from models import PlayerModel, GameModel, MatchModel, skillBase_names


class TemplatedView(RequestHandler):

    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, template, **context):
        """ Pass a template (html) and a dictionary :) """

        if "logout" not in context.keys() or "login" not in context.keys():
            user = users.get_current_user()
            if user:
                context["logout"] = users.create_logout_url("/")
            else:
                context["login"] = users.create_login_url("/")
        content = self.jinja2.render_template(template, **context)
        self.response.write(content)


class compareView(TemplatedView):

    def get(self):
        user = users.get_current_user()
        a = PlayerModel.query()
        name_list = dict([(i.key.id(), "%s %s" % (i.first_name, i.last_name) ) for i in a.iter()])
        self.render_response("compare.html", user=user, names=name_list.values(), keys=name_list.keys())

    def post(self):
        key = ndb.Key(PlayerModel, self.request.POST['selector'])
        a = key.get()
        user = self.request.POST["user"]
        stats = player_utils.compare_players(a, user)

        self.render_response('player.html', )


class errorHandler(TemplatedView):

    def get(self):
        path = self.request.path_qs[1:]
        self.render_response("error.html", error_message=path)


class mainView(TemplatedView):

    def get(self):
        user=users.get_current_user()
        if user:
            key = ndb.Key(PlayerModel, user.email())
            #a = PlayerModel(key=key)
            a = key.get()
            if a:
                a, b = utils.get_ladder()
                self.render_response('main.html', players=[i for i in a.iter()],
                    numplayers=a.count(), active=b.count(),
                    logout=users.create_logout_url("/"), name=user.nickname())
            else:
                table = []
                for i,j in skillBase_names.iteritems():
                    table.append([j,i])
                sorted(table, key=lambda tables: tables[0], reverse=True)
                a, b = utils.get_ladder()

                self.render_response('newPlayer.html',
                    names=skillBase_names.keys() , keys=skillBase_names.keys(),
                    keyVals=table,
                    nick=user.nickname(), playerKey=user.email(),
                    players=[i for i in a.iter()],
                    numplayers=a.count(), active=b.count())
        else:
            self.render_response('main2.html', login=users.create_login_url('/'))


class newPlayerView(TemplatedView):

    def get(self):
        user=users.get_current_user()
        key = ndb.Key(PlayerModel, user.email() )
        a = key.get()
        if a:
            a, b = utils.get_ladder()
            self.render_response('main.html', players=[i for i in a.iter()],
                numplayers=a.count(), active=b.count(),
                logout=users.create_logout_url("/"), name=user.nickname())
            #player = users.get_current_user()
            #table = []
            #for i,j in skillBase_names.iteritems():
            #    table.append([j,i])
            #table.sort()
            #self.render_response( 'newPlayer.html', table=table, names=skillBase_names.keys() , keys=skillBase_names.keys(), nick=player.nickname(), playerKey=player.email())

    def post(self):
        logging.debug("Starting new Player %s" % self.request.POST["key"] )
        key=""
        lname=""
        fname=""
        won=0
        played=0
        sscore=0
        if "key" in self.request.POST.keys():
            key= self.request.POST["key"]
        elif "skillBaseVal" in self.request.POST.keys():
            key= self.request.POST["skillBaseVal"]
        else:
            return None
        if "fname" in self.request.POST.keys():
            fname= self.request.POST["fname"]
        else:
            return None
        if "lname" in self.request.POST.keys():
            lname= self.request.POST["lname"]
        else:
            return None
        if "won" in self.request.POST.keys():
            won= int(self.request.POST["won"])
        if "played" in self.request.POST.keys():
            played=int( self.request.POST["played"])
        if "score" in self.request.POST.keys():
            sscore=int( self.request.POST["score"])

        keys = [ndb.Key(PlayerModel, key )]

        a = PlayerModel(key=keys[0])
        a.skillBase = self.request.POST['skillBaseVal']
        a.first_name = fname
        a.last_name = lname
        a.gamesPlayed = played
        a.gamesWon = won
        a.skillScore = int(skillBase_names[a.skillBase])
        logging.debug("Putting new Player %s" % key )
        a.put()
        self.redirect("/")


class playerView(TemplatedView):

    def get(self):
        a = PlayerModel.query()
        name_list = dict([(i.key.id(), "%s %s" % (i.first_name, i.last_name) ) for i in a.iter()])
        self.render_response("selector.html", names=name_list.values(), keys=name_list.keys())

    def post(self):
        key=ndb.Key(PlayerModel, self.request.POST['selector'])
        a = key.get()
        name, last, skill, wins, losses, games, win_ratio, last_five_games, \
            streak = player_utils.calc_player_info(a, key)
        logging.info("Displaying info on %s %s" % (name, last))
        self.render_response('player.html', name=name, last=last, skill=skill,
            wins=wins, losses=losses, games=games, win_ratio=win_ratio,
            last_five_games=last_five_games, streak=streak)

class playerStatsView(TemplatedView):

    def get(self):
        pKey = self.request.GET["key"]
        if pKey:
            key=ndb.Key(pKey)
            a = key.get()
            name, last, skill, wins, losses, games, win_ratio, last_five_games,\
            streak = player_utils.calc_player_info(a, key)
            logging.info("Displaying info on %s %s" % (name, last))
            self.render_response('player.html', name=name, last=last, skill=skill,
                wins=wins, losses=losses, games=games, win_ratio=win_ratio,
                last_five_games=last_five_games, streak=streak)
        else:
            self.render_response('error.html', error_message="Player %s does not exist" % pKey)

class reportView(TemplatedView):

    def get(self):
        keys = []
        a=PlayerModel.query()
        name_list= dict([(i.key.id(),"%s %s" % (i.first_name, i.last_name) )for i in a.iter()] )
        #        logging.info(name_list)
        #        logging.info("::::")
        user = users.get_current_user()
        self.render_response('reportGame.html', user=[name_list[user.email()], ], userKey=user.email() , names=name_list.values(), keys=name_list.keys())


class selectorView(TemplatedView):

    def get(self):
        a=PlayerModel.query()
        name_list= dict([(i.key.id(),"%s %s" % (i.first_name, i.last_name) )for i in a.iter()] )
        self.render_response('selector.html', names=name_list.values(), keys=name_list.keys())


class settingsView(TemplatedView):

    def get(self, form_success=None):
        user = users.get_current_user()
        if user is not None:
            key = ndb.Key(PlayerModel, user.email())
            a = key.get()
            name, last, skill, wins, losses, games, win_ratio, last_five_games,\
            streak = player_utils.calc_player_info(a, key)
            self.render_response("settings.html", user=a, key=user.email(), name=name, last=last, skill=skill,
                          wins=wins, losses=losses, games=games, win_ratio=win_ratio,
                           last_five_games=last_five_games, streak=streak,form_success=form_success)
        else:
            self.render_response("error.html", error_message=user)

    def post(self):
        if "key" in self.request.POST.keys():
            fname = self.request.POST["fname"]
            lname = self.request.POST["lname"]
            key = self.request.POST["key"]

            player_utils.update_player_name(key, fname, lname)

            self.get(form_success=True)

