from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.webapp._webapp25 import RequestHandler
from webapp2 import RequestHandler, cached_property
from webapp2_extras import jinja2
from models import PlayerModel, GameModel, MatchModel, skillBase_names
import logging
import utils

class TemplatedView(RequestHandler):

    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, template, **context):
        """ Pass a template (html) and a dictionary :) """
        content = self.jinja2.render_template(template, **context)
        self.response.write(content)


class selectorView(TemplatedView):

    def get(self):
        keys = []
        a=PlayerModel.query()
        name_list= dict([(i.key.id(),"%s %s" % (i.first_name, i.last_name) )for i in a.iter()] )
        logging.info(name_list)
        logging.info("::::")
        self.render_response('selector.html', names=name_list.values(), keys=name_list.keys())


class reportView(TemplatedView):

    def get(self):
        keys = []
        a=PlayerModel.query()
        name_list= dict([(i.key.id(),"%s %s" % (i.first_name, i.last_name) )for i in a.iter()] )
        logging.info(name_list)
        logging.info("::::")
        user = users.get_current_user()
        self.render_response('reportGame.html', user=[name_list[user.email()], ], userKey=[user.email()] , names=name_list.values(), keys=name_list.keys())


class playerView(TemplatedView):

    def get(self):
        a = PlayerModel.query()
        name_list = dict([(i.key.id(), "%s %s" % (i.first_name, i.last_name) ) for i in a.iter()])
        self.render_response("selector.html", names=name_list.values(), keys=name_list.keys())

    def post(self):
        key=ndb.Key(PlayerModel, self.request.POST['selector'])
        a = key.get()
        self.render_response('player.html', name=a.first_name, last=a.last_name,skill=a.skillScore, wins=a.gamesWon, loses=(a.gamesPlayed - a.gamesWon) )


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
        self.get()


class mainView(TemplatedView):

    def get(self):
        user=users.get_current_user()
        if user:
            key = ndb.Key(PlayerModel, user.email() )
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

class errorHandler(TemplatedView):

    def get(self, error):
        self.render_response("error.html", error_message=error)
