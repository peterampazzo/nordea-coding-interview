import os
import pandas as pd
import json
import uuid

class PyFootball:

    PATH_DATA = 'data/'
    PATH_OUTPUT = 'output/'
    DATAFRAME = 'events.csv'
    MATCH_TOTAL_MINUTES = 90

    @staticmethod
    def get_team_score(df: 'pandas.core.frame.DataFrame', match_id: int, is_home: bool) -> int:
        '''
        Given the match_id return the score of the home/away team
        '''

        df_match = df[(df['match_id'] == match_id) & (df['is_home'] == is_home)]
        score = df_match['goals_scored'].sum()

        return int(score)

    @staticmethod
    def get_team_id(df: 'pandas.core.frame.DataFrame', match_id: int, is_home: bool) -> int:
        '''
        Given the match_id return the team_id of the home/away team
        '''

        df_match = df[(df['match_id'] == match_id) & (df['is_home'] == is_home)]
        team_id = df_match.iloc[0, df_match.columns.get_loc('team_id')]  # Get 'team_id' from the first row

        return int(team_id)

    @staticmethod
    def get_player_fraction_of_total_goals_scored(player_goals: int, match_goals: int) -> float:
        '''
        Given the number of goals of one player and the total amout of goals return the rounded fraction of total goals scored
        '''

        return round(player_goals / match_goals, 2) if player_goals != 0 else 0 

    @staticmethod
    def get_player_fraction_of_total_minutes_played(minutes_played: int) -> float:
        '''
        Given the number of minutes played by a player return the rounded fraction of total minuted played
        '''

        return round(minutes_played/PyFootball.MATCH_TOTAL_MINUTES, 2)

    @staticmethod
    def save_jsonline(filename: str, data: list) -> None:
        '''
        Save JSON Lines file: a filename and a list of JSONs must be passed
        '''

        path_json = os.path.join(PyFootball.PATH_OUTPUT, filename + '.jsonl')

        with open(path_json, 'w') as outfile:
            for entry in data:
                json.dump(entry, outfile)
                outfile.write('\n')

        print(f'File generated:', filename)

    @staticmethod
    def row_to_dict(output: str, data: list) -> dict:
        '''
        Given the type of output (match/team/player/stat) and the parsed data from a row return a dict
        '''

        if output == 'match':
            return {
                'match_id':     data[0],
                'match_name':   data[1],
                'home_team_id': data[2],
                'away_team_id': data[3],
                'home_goals':   data[4],
                'away_goals':   data[5]
            }
        elif output == 'team':
            return {
                'team_id':      data[0],
                'team_name':    data[1]
            }
        elif output == 'player':
            return {
                'player_id':    data[0],
                'team_id':      data[1],
                'player_name':  data[2]
            }
        elif output == 'stat':
            return {
                'stat_id':                          data[0],
                'player_id':                        data[1],
                'match_id':                         data[2],
                'goal_scored':                      data[3],
                'minutes_played':                   data[4],
                'fraction_of_total_minutes_played': data[5],
                'fraction_of_total_goals_scored':   data[6]
            }
        else:
            return {}

    @staticmethod
    def parse_row(df: 'pandas.core.frame.DataFrame', row: list) -> (dict, dict, dict, dict):
        '''
        Given data set and a row return the output dicts (match/team/player/stat)
        '''
    
        # Teams ID
        home_team = PyFootball.get_team_id(df, row['match_id'], is_home = True)
        away_team = PyFootball.get_team_id(df, row['match_id'], is_home = False)

        # Match scores
        home_score = PyFootball.get_team_score(df, row['match_id'], is_home = True)
        away_score = PyFootball.get_team_score(df, row['match_id'], is_home = False)

        # Fraction of total
        fraction_of_total_goals_scored = PyFootball.get_player_fraction_of_total_goals_scored(row['goals_scored'], (home_score + away_score))
        fraction_of_total_minutes_played = PyFootball.get_player_fraction_of_total_minutes_played(row['minutes_played'])

        # Generate stat_id
        stat_id = uuid.uuid1().hex

        # Generate JSON (dict)
        match  = PyFootball.row_to_dict('match', [row['match_id'], row['match_name'], home_team, away_team, home_score, away_score])
        team   = PyFootball.row_to_dict('team', [row['team_id'], row['team_name']])
        player = PyFootball.row_to_dict('player', [row['player_id'], row['team_id'], row['player_name']])
        stat   = PyFootball.row_to_dict('stat', [stat_id, row['player_id'], row['match_id'], row['goals_scored'], row['minutes_played'], fraction_of_total_minutes_played, fraction_of_total_goals_scored])

        return (match, team, player, stat)

    @staticmethod
    def run(filename: str, drop_duplicates : bool = False) -> (dict, dict, dict, dict):
        '''
        Load data, run parser and return JSON Lines
        If 'drop_duplicates' is True all the duplicates in matches/teams/players are dropped
        '''

        df = pd.read_csv(filename)

        # Unique ids
        teams = []
        players = []
        matches = []

        # Output
        out_matches = []
        out_teams = []
        out_players = []
        out_stats = []

        # Loop through every row in the data set
        for index, row in df.iterrows():
            row_match, row_team, row_player, row_stat = PyFootball.parse_row(df, row)

            if drop_duplicates:
                player = row['player_id']
                team   = row['team_id']
                match  = row['match_id']

                if player not in players:
                    players.append(player)
                    out_players.append(row_player)
                if team not in teams:
                    teams.append(team)
                    out_teams.append(row_team)
                if match not in matches:
                    matches.append(match)
                    out_matches.append(row_match)
            else:
                out_teams.append(row_team)
                out_players.append(row_player)
                out_matches.append(row_match)

            out_stats.append(row_stat)

        return (out_matches, out_teams, out_players, out_stats)

if __name__ == '__main__':
    path_csv = os.path.join(PyFootball.PATH_DATA, PyFootball.DATAFRAME)

    # Check if file exists
    if os.path.exists(path_csv):
        # Create 'output' folder if does not exist
        if not os.path.exists(PyFootball.PATH_OUTPUT):
            os.mkdir(PyFootball.PATH_OUTPUT)

        matches, teams, players, stats = PyFootball.run(path_csv, drop_duplicates = True) # Set to False if not drop duplicates

        # Save output to JSON Lines files
        PyFootball.save_jsonline('match', matches)
        PyFootball.save_jsonline('team', teams)
        PyFootball.save_jsonline('player', players)
        PyFootball.save_jsonline('statistic', stats)
    else:
        print(f'File not found:', path_csv)