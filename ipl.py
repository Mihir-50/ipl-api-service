# In this file we write logic for Data Analysis
import numpy as np
import pandas as pd
import json



# Using below link I am uploading the data
ipl_matches = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
matches = pd.read_csv(ipl_matches)

ipl_ball = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"
balls = pd.read_csv(ipl_ball)



# Applying Inner Join
ball_withmatch = balls.merge(matches, on='ID', how='inner')
# Creating a seperate column name 'BowlingTeam' and adding both team with each other without any space b/w them
ball_withmatch['BowlingTeam'] = ball_withmatch['Team1'] + ball_withmatch['Team2']
# Using lambda function for seperating 'Batting Team' & 'Bowling Team' and showing each of them in their respective column
ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(lambda x: x.values[0].replace(x.values[1], ''), axis=1)
# appending ['BowlingTeam', 'Player_of_Match'] in balls.columns.values(which is an array) and fetch columns(array) from ball_withmatch
batter_data = ball_withmatch[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]





# to get all team names
def allteamsAPI():
    teams = list(set(list(matches['Team1']) + list(matches['Team2'])))
    team_dict = {
        'teams':teams
    }
    return team_dict



# to get info b/w two teams
def teamVSteamAPI(team1,team2):
    valid_teams = list(set(list(matches['Team1']) + list(matches['Team2'])))

    if (team1 in valid_teams) and (team2 in valid_teams):
        temp_df = matches[((matches['Team1'] == team1) & (matches['Team2'] == team2)) | ((matches['Team2'] == team1) & (matches['Team1'] == team2))]

        total_matches = temp_df.shape[0]
        try:
            won_team1 = temp_df['WinningTeam'].value_counts()[team1]
        except:
            won_team1 = 0

        try:
            won_team2 = temp_df['WinningTeam'].value_counts()[team2]
        except:
            won_team2 = 0

        draws = total_matches - (won_team1 + won_team2)

        response = {'matches_played': str(total_matches),
                     team1          : str(won_team1),
                     team2          : str(won_team2),
                     'draws'        : str(draws)
                    }
        return response

    else:
        return {
            'message':'invalid team name'
        }



# all records of a team throughout the IPL
def allRecordAPI(team):
    df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)]

    match_played = df.shape[0]
    won = df[df['WinningTeam'] == team].shape[0]
    no_result = df[df['WinningTeam'].isnull()].shape[0]
    loss = match_played - (won + no_result)
    won_IPL = df[(df['MatchNumber'] == 'Final') & (df['WinningTeam'] == team)].shape[0]

    return {'matchesplayed': match_played,
            'won'          : won,
            'loss'         : loss,
            'noResult'     : no_result,
            'title'        : won_IPL}



# to get info about any team
def teamAPI(team):

    self_record = allRecordAPI(team)
    TEAMS = matches['Team1'].unique()
    against = {t: teamVSteamAPI(team, t) for t in TEAMS}
    print(against)

    data = {team: {'overall': self_record,
                   'against': against
                   }
            }
    return json.dumps(data)



# this is use to tell the record of a batsman in IPL
def batsmanRecord(batsman, df):
    if df.empty:
        return np.nan
    out = df[df.player_out == batsman].shape[0]
    df = df[df['batter'] == batsman]
    inngs = df.ID.unique().shape[0]
    runs = df.batsman_run.sum()
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
    if out:
        avg = runs / out
    else:
        avg = np.inf

    nballs = df[~(df.extra_type == 'wides')].shape[0]
    if nballs:
        strike_rate = runs / nballs * 100
    else:
        strike_rate = 0
    gb = df.groupby('ID').sum(numeric_only=True)
    fifties = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
    hundreds = gb[gb.batsman_run >= 100].shape[0]
    try:
        highest_score = gb.batsman_run.sort_values(ascending=False).head(1).values[0]
        hsindex = gb.batsman_run.sort_values(ascending=False).head(1).index[0]
        if (df[df.ID == hsindex].player_out == batsman).any():
            highest_score = str(highest_score)
        else:
            highest_score = str(highest_score) + '*'
    except:
        highest_score = gb.batsman_run.max()

    not_out = inngs - out
    mom = df[df.Player_of_Match == batsman].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'innings'     : str(inngs),
        'runs'        : str(runs),
        'fours'       : str(fours),
        'sixes'       : str(sixes),
        'avg'         : str(avg),
        'strikeRate'  : str(strike_rate),
        'fifties'     : str(fifties),
        'hundreds'    : str(hundreds),
        'highestScore': str(highest_score),
        'notOut'      : str(not_out),
        'mom'         : str(mom)
    }

    return data


# this is use to tell the record of a batsman against every team in IPL
def batsmanVsTeam(batsman, team, df):
    df = df[df.BowlingTeam == team]
    return batsmanRecord(batsman, df)


# use to find record of batsman in IPL as well as against a particular team
def batsmanAPI(batsman, balls=batter_data):
    # Excluding Super overs
    df = balls[balls.innings.isin([1, 2])]
    self_record = batsmanRecord(batsman, df=df)
    TEAMS = matches.Team1.unique()
    against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
    data = {
        batsman: {'all'    : self_record,
                  'against': against
                  }
    }
    return json.dumps(data)




bowler_data = batter_data.copy()


def bowlerRun(x):
    if x[0] in ['penalty', 'legbyes', 'byes']:
        return 0
    else:
        return x[1]
bowler_data['bowler_run'] = bowler_data[['extra_type', 'total_run']].apply(bowlerRun, axis=1)


def bowlerWicket(x):
    if x[0] in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']:
        return x[1]
    else:
        return 0
bowler_data['isBowlerWicket'] = bowler_data[['kind', 'isWicketDelivery']].apply(bowlerWicket, axis=1)


# this is use to tell the record of a bowler in IPL
def bowlerRecord(bowler, df):

    df = df[df['bowler'] == bowler]
    inngs = df.ID.unique().shape[0]
    nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs = df['bowler_run'].sum()
    if nballs:
        eco = runs / nballs * 6
    else:
        eco = 0
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]

    wicket = df.isBowlerWicket.sum()
    if wicket:
        avg = runs / wicket
    else:
        avg = np.inf

    if wicket:
        strike_rate = nballs / wicket * 100
    else:
        strike_rate = np.nan

    gb = df.groupby('ID').sum()
    w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]

    best_wicket = gb.sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True])[
        ['isBowlerWicket', 'bowler_run']].head(1).values
    if best_wicket.size > 0:

        best_figure = f'{best_wicket[0][0]}/{best_wicket[0][1]}'
    else:
        best_figure = np.nan
    mom = df[df.Player_of_Match == bowler].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'innings'    : str(inngs),
        'wicket'     : str(wicket),
        'economy'    : str(eco),
        'average'    : str(avg),
        'avg'        : str(avg),
        'strikeRate' : str(strike_rate),
        'fours'      : str(fours),
        'sixes'      : str(sixes),
        'best_figure': str(best_figure),
        '3+W'        : str(w3),
        'mom'        : str(mom)
    }

    return data


# this is use to tell the record of a bowler against every team in IPL
def bowlerVsTeam(bowler, team, df):
    df = df[df.BattingTeam == team].copy()
    return bowlerRecord(bowler, df)


# use to find record of bowler in IPL as well as against a particular team
def bowlerAPI(bowler, balls=bowler_data):
    # Excluding Super overs
    df = balls[balls.innings.isin([1, 2])]
    self_record = bowlerRecord(bowler, df=df)
    TEAMS = matches.Team1.unique()
    against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
    data = {
        bowler: {'all'    : self_record,
                 'against': against}
    }
    return json.dumps(data)