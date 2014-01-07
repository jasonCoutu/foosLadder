import logging

from google.appengine.api import users
from webapp2 import RequestHandler, cached_property
from webapp2_extras import jinja2

import json
import app.utils as utils
import app.utils.player_utils as player_utils
import app.domain.player as player_dom
from app.domain import skillBase_names as skillBase_function


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


class aboutView(TemplatedView):

    def get(self):
        self.render_response("about.html")


class compareView(TemplatedView):

    def get(self):
        user = users.get_current_user()
        a = player_dom.get_entities()
        name_list = dict([(i.key.id(), "%s %s" % (i.first_name, i.last_name) ) for i in a.iter()])
        self.render_response("compare.html", user=user, names=name_list.values(), keys=name_list.keys())

    def post(self):
        player_key = player_dom.get_key(self.request.POST['selector'])
        user = self.request.POST["user"]
        stats = player_utils.compare_players(player_key, user)

        # unused
        self.render_response('player.html', )


class errorHandler(TemplatedView):

    def get(self):
        path = self.request.path_qs[1:]
        self.render_response("error.html", error_message=path)


class ladderRedirect(TemplatedView):

    def get(self):
        """
        Redirect to the ladder, fix/avoid the "refresh match resubmit" bug
        """
        self.redirect("/ladder")


class leaderboardView(TemplatedView):

    def get(self):
        # get stats
        highest_goals = player_utils.get_highest_goals()
        highest_goals_against = player_utils.get_highest_goals(against=True)
        highest_wins = player_utils.get_most_games(calc_type="wins")
        highest_games = player_utils.get_most_games()
        highest_losses = player_utils.get_most_games(calc_type="losses")
        self.render_response("leaderboard.html", goals=highest_goals,
                             goals_against=highest_goals_against,
                             wins=highest_wins,
                             losses=highest_losses, games=highest_games)


class mainView(TemplatedView):

    def get(self):
        user = users.get_current_user()
        if user:
            a = player_dom.get_by_email(user.email())
            if a:
                players_total, actives = utils.get_ladder()
                user = users.get_current_user()
                player_list = []

                for players in players_total.iter():
                    player_list.append((players.key.id(),
                                        "%s %s" % (players.first_name,
                                                   players.last_name),
                                        players.skillScore))
                self.render_response('main.html',
                                     players=player_list,
                                     numplayers=players_total.count(),
                                     active=actives.count(),
                                     user=user, name=user.nickname())
            else:
                skillBase_names = skillBase_function()
                table = []
                for i, j in skillBase_names.iteritems():
                    table.append([j, i])
                sorted(table, key=lambda tables: tables[0], reverse=True)
                a, b = utils.get_ladder()

                self.render_response('newPlayer.html',
                                     names=skillBase_names.keys(),
                                     keys=skillBase_names.keys(),
                                     keyVals=table,
                                     nick=user.nickname(),
                                     playerKey=user.email(),
                                     players=[i for i in a.iter()],
                                     numplayers=a.count(),
                                     active=b.count(),
                                     new=True)
        else:
            self.render_response('main2.html',
                                 login=users.create_login_url('/'))


class matchHistoryCalc(TemplatedView):

    def get(self):
        email = self.request.GET["email"]
        returnData = player_utils.match_history(email)
        self.response.out.write(json.dumps(returnData))


class matchHistoryView(TemplatedView):

    def get(self):
        user = users.get_current_user()
        a = player_dom.get_entities()
        name_list = dict([(i.key.id(),
                           "%s %s" % (i.first_name, i.last_name))
                          for i in a.iter()])
        self.render_response("matchhistory.html",
                             user=user,
                             names=name_list.values(),
                             keys=name_list.keys())

    def post(self, *args):
        arg_list = args
        name = self.request.POST
        self.render_response("matchhistory.html",
                             selected=True,
                             arglist=arg_list)


class newPlayerView(TemplatedView):

    def get(self):
        user = users.get_current_user()
        a = player_dom.get_by_email(user.email())
        if a:
            a, b = utils.get_ladder()
            self.render_response('main.html',
                                 players=[i for i in a.iter()],
                                 numplayers=a.count(),
                                 active=b.count(),
                                 logout=users.create_logout_url("/"),
                                 name=user.nickname())

    def post(self):
        logging.debug("Starting new Player %s" % self.request.POST["key"])
        won = 0
        played = 0
        sscore = 0
        if "key" in self.request.POST.keys():
            key = self.request.POST["key"]
        elif "skillBaseVal" in self.request.POST.keys():
            key = self.request.POST["skillBaseVal"]
        else:
            return None
        if "fname" in self.request.POST.keys():
            fname = self.request.POST["fname"]
        else:
            return None
        if "lname" in self.request.POST.keys():
            lname = self.request.POST["lname"]
        else:
            return None
        if "won" in self.request.POST.keys():
            won = int(self.request.POST["won"])
        if "played" in self.request.POST.keys():
            played = int(self.request.POST["played"])
        if "score" in self.request.POST.keys():
            score = int(self.request.POST["score"])

        player = dict()
        player["skillBase"] = self.request.POST['skillBaseVal']
        player["first_name"] = fname
        player["last_name"] = lname
        player["gamesPlayed"] = played
        player["gamesWon"] = won
        player["skillScore"] = int(skillBase_function()[player["skillBase"]])
        logging.debug("Putting new Player %s" % key)
        success = player_dom.new_player(key, fname, lname,
                                        player["skillScore"],
                                        player["skillBase"])
        if success:
            self.redirect("/")


class playerView(TemplatedView):

    def get(self):
        a = player_dom.get_entities()
        name_list = dict([(i.key.id(), "%s %s" % (i.first_name, i.last_name) ) for i in a.iter()])
        self.render_response("selector.html", names=name_list.values(), keys=name_list.keys())

    def post(self):
        a = player_dom.get_by_email(self.request.POST['selector'])
        key = player_dom.get_key(self.request.POST['selector'])
        one_player = player_utils.calc_player_info(a, key)
        logging.info("Displaying info on %s %s" % (one_player["name"],
                                                   one_player["last"]))
        self.render_response('player.html', player=one_player, key=key.id())


class playerStatsView(TemplatedView):

    def get(self):
        pKey = self.request.GET["key"]
        if pKey:
            key = player_dom.get_key(str(pKey))
            a = player_dom.get_by_email(str(pKey))
            one_player = player_utils.calc_player_info(a, key)
            user = users.get_current_user()
            logging.info("Displaying info on %s %s" % (one_player["name"],
                                                       one_player["last"]))
            self.render_response('player.html', player=one_player, key=pKey,
                                 user=user)
        else:
            self.render_response('error.html',
                                 error_message="Player %s does not exist" %
                                               pKey)


class reportView(TemplatedView):

    def get(self):
        a = player_dom.get_entities()
        name_list = dict([(i.key.id(),
                           "%s %s" % (i.first_name, i.last_name))
                          for i in a.iter()])
        #        logging.info(name_list)
        #        logging.info("::::")
        user = users.get_current_user()
        # If they're logged in, let them report a game
        if user:
            try:
                oppKey = self.request.GET["oppKey"]
                self.render_response('reportGame.html',
                                     user=[name_list[user.email()], ],
                                     userKey=user.email(),
                                     names=name_list.values(),
                                     keys=name_list.keys(), key=oppKey)
            except KeyError:
                self.render_response('reportGame.html',
                                     user=[name_list[user.email()]],
                                     userKey=user.email(),
                                     names=name_list.values(),
                                     keys=name_list.keys())
        # If they are not logged in, show the "not logged in" front page
        else:
            self.render_response('main2.html',
                                 login=users.create_login_url('/'))


class selectorView(TemplatedView):

    def get(self):
        a = player_dom.get_entities()
        name_list = dict([(i.key.id(),
                           "%s %s" % (i.first_name, i.last_name))
                          for i in a.iter()])
        self.render_response('selector.html',
                             names=name_list.values(),
                             keys=name_list.keys())


class settingsView(TemplatedView):

    def get(self, form_success=None):
        user = users.get_current_user()
        if user is not None:
            key = player_dom.get_key(user.email())
            a = player_dom.get_by_email(user.email())
            one_player = player_utils.calc_player_info(a, key)
            self.render_response("settings.html",
                                 user=a,
                                 key=one_player["email"],
                                 player=player_dom,
                                 form_success=form_success)
        else:
            self.render_response("error.html", error_message=user)

    def post(self):
        if "key" in self.request.POST.keys():
            fname = self.request.POST["fname"]
            lname = self.request.POST["lname"]
            key = self.request.POST["key"]

            success = player_utils.update_player_name(fname, lname, key)

            if success:
                self.get(form_success=True)
            else:
                self.get(form_success=False)

