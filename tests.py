import unittest
import pandas as pd
from main import PyFootball

class TestPyFootball(unittest.TestCase):
    def setUp(self):
        self.parser = PyFootball
        self.path = 'data/test.csv'
        self.df = pd.read_csv(self.path)

    def test_get_home_team_score(self):
        result = self.parser.get_team_score(self.df, 1, True)
        self.assertEqual(result, 15)

    def test_get_away_team_score(self):
        result = self.parser.get_team_score(self.df, 10, False)
        self.assertEqual(result, 16)

    def test_get_home_team_id(self):
        result = self.parser.get_team_id(self.df, 10, True)
        self.assertEqual(result, 12)

    def test_get_away_team_id(self):
        result = self.parser.get_team_id(self.df, 1, False)
        self.assertEqual(result, 12)

    def test_player_fraction_of_total_goals_scored(self):
        subtests = [
            # (player_goals, team_goals, fraction_of_total_goals_scored)
            (1, 10, 0.1),
            (5, 5, 1),
            (1, 2, 0.5),
            (3, 20, 0.15)
        ]

        for i, test in enumerate(subtests):
            player_goals, team_goals, output = test
            with self.subTest(i=i):
                result = self.parser.get_player_fraction_of_total_goals_scored(player_goals, team_goals)
                self.assertEqual(result, output)

    def test_player_fraction_of_total_minutes_played(self):
        subtests = [
            # (played_minutes, fraction_of_total_minutes_played)
            (45, 0.5),
            (90, 1),
            (15, 0.17),
            (18, 0.2),
            (36, 0.4)
        ]
        for i, test in enumerate(subtests):
            played_minutes, output = test
            with self.subTest(i=i):
                result = self.parser.get_player_fraction_of_total_minutes_played(played_minutes)
                self.assertEqual(result, output)

    def test_run_without_duplicates(self):
        matches, teams, players, stats = PyFootball.run(self.path, drop_duplicates = True)
        self.assertEqual(len(matches), 2)
        self.assertEqual(len(teams), 3)
        self.assertEqual(len(players), 15)

    def test_run_with_duplicates(self):
        matches, teams, players, stats = PyFootball.run(self.path, drop_duplicates = False)
        self.assertEqual(len(matches), 20)
        self.assertEqual(len(teams), 20)
        self.assertEqual(len(players), 20)
        
if __name__ == '__main__':
    unittest.main()
