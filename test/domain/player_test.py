from app.domain.player import get_entities, get_by_email, get_key, \
    get_multi_players, get_players_sorted_skill_score, get_active_players, \
    new_player, update_player_name

from test.fixtures.appengine import GaeTestCase
from unittest import TestCase


class NewPlayerTests(TestCase):

    def setUp(self):
        self.firstname = "Test"
        self.lastname = "Last"
        self.email = "test@email.com"
        self.skillScore = 500
        self.skillBase = "Class C"

    def test_email_required(self):
        self.assertRaises(ValueError, new_player, None, None, None, None, None)

    def test_first_name_required(self):
        self.assertRaises(ValueError, new_player, self.email, None, None, None,
                          None)

    def test_last_name_required(self):
        self.assertRaises(ValueError, new_player, self.email, self.firstname,
                          None, None, None)

    def test_skill_score_required(self):
        self.assertRaises(ValueError, new_player, self.email, self.firstname,
                          self.lastname, None, None)

    def test_skill_base_required(self):
        self.assertRaises(ValueError, new_player, self.email, self.firstname,
                          self.lastname, self.skillScore, None)

    # def test_player_created_successfully(self):
    #     player = new_player(self.email, self.firstname,
    #                         self.lastname, self.skillScore, self.skillBase)
    #     self.assertEqual(player.email, self.email)
    #     self.assertEqual(player.first_name, self.firstname)
    #     self.assertEqual(player.last_name, self.lastname)
    #     self.assertEqual(player.skillScore, self.skillScore)
    #     self.assertEqual(player.skillBase, self.skillBase)


class UpdateNameTests(TestCase):

    def setUp(self):
        self.firstname = "Test"
        self.lastname = "Test"
        self.email = "test@email.com"

    def test_email_required(self):
        self.assertRaises(ValueError, update_player_name, self.firstname,
                          self.lastname, None)

    def test_first_name_required(self):
        self.assertRaises(ValueError, update_player_name, None, None, None)

    def test_last_name_required(self):
        self.assertRaises(ValueError, update_player_name, self.firstname, None,
                          None)