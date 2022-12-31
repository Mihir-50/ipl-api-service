from flask import Flask,jsonify,request
import ipl

app = Flask(__name__)

@app.route('/')
def home():
    return 'An API service for IPL cricket matches'



# 1st API in Flask Application which tells total teams participated in IPL
@app.route('/api/teams')
def teams():
    # below code is to access data inside teamsAPI function which is in ipl.py module, which return a dictionary
    teams = ipl.allteamsAPI()
    # As API return JSON import jsonify to convert dictionary to JSON
    return jsonify(teams)



# 2nd API which tell name of all batsmans in IPL
@app.route('/api/batsmans')
def batsmans():
    batsmans = ipl.allbatsmanAPI()
    return jsonify(batsmans)



# 3rd API which tell name of all bowlers in IPL
@app.route('/api/bowlers')
def bowlers():
    bowlers = ipl.allbowlerAPI()
    return jsonify(bowlers)



# 4th API in Flask, which takes two input i.e., team names & tells record b/w each other
# Two ways to take data to server (i) post (ii) get
# If we want to send the data by hiding it in URL, use 'post'. Example : password, credit card info etc.
# If we want to send using URL, use 'get'
# Request: Use to receive data which we have inputted into URL in API, inside below function
@app.route('/api/teamvsteam')
def teamvsteam():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    response = ipl.teamVSteamAPI(team1,team2)
    return response


# 5th API in Flask for team record
@app.route('/api/team-record')
def team_record():
    team_name = request.args.get('team')
    response = ipl.teamAPI(team_name)
    return response



# 6th API in Flask for batsman record
@app.route('/api/batsman-record')
def batsman_record():
    batsman_name = request.args.get('batsman')
    response = ipl.batsmanAPI(batsman_name)
    return response


# 7th API in Flask for bowler record
@app.route('/api/bowler-record')
def bowler_record():
    bowler_name = request.args.get('bowler')
    response = ipl.bowlerAPI(bowler_name)
    return response



app.run(debug=True)