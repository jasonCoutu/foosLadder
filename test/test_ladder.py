import unittest

from utils import *

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.player_a = 1400

    def test_elo_high_low(self):
        player_b = 1000

        player_a, player_b = calculate_elo_rank(self.player_a, player_b, self.player_a, True)

        self.assertEqual(player_a, 1403)

    def test_elo_high_low_2(self):
        player_b = 997

        player_a, player_b = calculate_elo_rank(self.player_a, player_b, self.player_a, True)

        self.assertEqual(player_a, 1400)

if __name__ == '__main__':
    unittest.main()