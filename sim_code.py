import pandas as pd
import numpy as np
import random
from ipywidgets import interact_manual, widgets
from collections import Counter, defaultdict
# Sim assumes:
# 1. Each point is i.i.d (independent, identically, distributed).
# 2. Player ability is independent of pressure.
# 3. Player distribution is approximately normal if they have $>= 1000$ service points.
# 4. All matches played are based on the players "normal" serve/return ability.
# 5. All surfaces are independent of each tournament they are played on (e.g. U.S. Open hard court versus Australian Open hard court is negligible).
# 6. Player ability is independent of different factors such as mental and physical state on each point.
# Function that can read data in for any year
def read_data(yr): 
    atp_data = pd.read_csv(f"atp_matches_{yr}.csv")
    atp_data['league'] = "ATP" 
    # Select columns from data set
    atp_data = atp_data[
        ['winner_name', 'loser_name', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_df',
         'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_df',
         'league', 'surface']]

    wta_data = pd.read_csv(f"wta_matches_{yr}.csv")
    wta_data['league'] = "WTA"
    wta_data = wta_data[
        ['winner_name', 'loser_name', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_df',
         'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_df',
         'league', 'surface']]

    data = pd.concat([atp_data, wta_data])
    return data
data = read_data(2023)
data.dropna(inplace=True) # Remove all NAs
winners = data[['winner_name', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_df',
                'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_df',
                'league', 'surface']]
losers = data[['loser_name', 'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_df',
               'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_df',
               'league', 'surface']]
# Change colnames
winners = winners.rename(columns={
    'winner_name': 'name',
    'w_svpt': 'svpt',
    'w_1stIn': 'fs_in',
    'w_1stWon': 'fs_win',
    'w_2ndWon': 'ss_win',
    'w_df': 'df',
    'l_svpt': 'o_svpt',
    'l_1stIn': 'o_fs_in',
    'l_1stWon': 'o_fs_win',
    'l_2ndWon': 'o_ss_win',
    'l_df': 'o_df'
})
losers = losers.rename(columns={
    'loser_name': 'name',
    'l_svpt': 'svpt',
    'l_1stIn': 'fs_in',
    'l_1stWon': 'fs_win',
    'l_2ndWon': 'ss_win',
    'l_df': 'df',
    'w_svpt': 'o_svpt',
    'w_1stIn': 'o_fs_in',
    'w_1stWon': 'o_fs_win',
    'w_2ndWon': 'o_ss_win',
    'w_df': 'o_df'
})
df = pd.concat([winners, losers]) # Bind rows
grouped_data = df.groupby(['name', 'league', 'surface']).sum().reset_index() # Sum over all variables after grouping by name, league and surface
grouped_data = grouped_data[grouped_data['svpt'] > 1000] # Filter out < 1000 observations
# Calculate player rate stats
grouped_data['fs_in_pct'] = grouped_data['fs_in'] / grouped_data['svpt']
grouped_data['fs_win_pct'] = grouped_data['fs_win'] / grouped_data['fs_in']
grouped_data['ss_in_pct'] = 1 - (grouped_data['df'] / (grouped_data['svpt'] - grouped_data['fs_in']))
grouped_data['ss_win_pct'] = grouped_data['ss_win'] / (grouped_data['svpt'] - grouped_data['fs_in'] - grouped_data['df'])
grouped_data['fr_win_pct'] = 1 - (grouped_data['o_fs_win'] / grouped_data['o_fs_in'])
grouped_data['sr_win_pct'] =  1 - (grouped_data['o_ss_win'] / (grouped_data['o_svpt'] - grouped_data['o_fs_in'] - grouped_data['o_df']))
# Create grouped data frame
df = grouped_data[['name', 'league', 'surface', 'fs_in_pct', 'fs_win_pct', 'ss_in_pct', 'ss_win_pct', 'fr_win_pct', 'sr_win_pct']] 
# Create a function that loops the action of a point
def loop_point(server_prob, returner_prob):
    while True: #While loop to infinitely iterate until the server/return prob are True
        # If random uniform value <= server prob, server wins and loop breaks
        if (np.random.uniform(low=0, high=1, size = None) <= server_prob):
            return('server')
            break
        elif (np.random.uniform(low=0, high=1, size = None) <= returner_prob):
            return('returner')
            break
# Create a function that simulates a point
# Accounting for likelihood of a first/second serve being in and the server/returner winning on a first/second serve based on serve in play
def sim_point(server, 
              p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,
              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win
             ):
    if server == 'p1': # If the server is p1, sim point for that server
        if (np.random.uniform(low=0, high=1, size = None) <= p1_fs_in):
            res = loop_point(p1_fs_win, p2_fr_win)
            if res == 'server':
                return('p1')
            else:
                return('p2')
        elif (np.random.uniform(low=0, high=1, size = None) <= p1_ss_in):
            res = loop_point(p1_ss_win, p2_sr_win)
            if res == 'server':
                return('p1')
            else:
                return('p2')
        else:
            return('p2')
    elif server == 'p2':
        if (np.random.uniform(low=0, high=1, size = None) <= p2_fs_in):
            res = loop_point(p2_fs_win, p1_fr_win)
            if res == 'server':
                return('p2')
            else:
                return('p1')
        elif (np.random.uniform(low=0, high=1, size = None) <= p2_ss_in):
            res = loop_point(p2_ss_win, p1_sr_win)
            if res == 'server':
                return('p2')
            else:
                return('p1')
        else:
            return('p1')
# Simulate a game
def sim_game(server, scoring, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,
              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win):
    p1_score = 0
    p2_score = 0
    while True: # Iterate a game over multiple points
        winner = sim_point(server, 
              p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,
              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win
             )
        if winner == 'p1':
            p1_score += 1
        else:
            p2_score += 1
        if scoring == 'ad': # If playing ad scoring
            # One player needs to have at least 4 points and "win by 2"
            if max(p1_score, p2_score) >= 4 and abs(p1_score - p2_score) >= 2:
                break
        elif scoring == 'no-ad':
            # If no-ad, first to 4 points
            if max(p1_score, p2_score) == 4:
                break
    return 'p1' if p1_score > p2_score else 'p2'
# Simulate the actions of a tiebreak
def sim_tb(server, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,
              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win):
    p1_points = 0
    p2_points = 0
    current_server = server # Based on first set server - later function input
    
    while True:
        # Simulate a point
        winner = sim_point(current_server, 
              p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,
              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win
             )
        
        # Update scores
        if winner == 'p1':
            p1_points += 1
        else:
            p2_points += 1
        
        # Check win condition
        if max(p1_points, p2_points) >= 7 and abs(p1_points - p2_points) >= 2:
            break
        
        # Alternate server every two points
        if (p1_points + p2_points) % 2 == 0:
            current_server = 'p1' if current_server == 'p2' else 'p2'
    
    # Return the winner of the tiebreaker
    return 'p1' if p1_points > p2_points else 'p2'
# Simulate an individual set
def sim_set(scoring, server, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,
              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win):
    # Initialize player games
    p1_games = 0
    p2_games = 0
    
    while True:
        # Simulate a game
        if p1_games == 6 and p2_games == 6:
            # If both players have won 6 games, play a tiebreaker
            winner = sim_tb(server, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,
              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win)
            if winner == 'p1':
                p1_games += 1
            else:
                p2_games += 1
            break
        else:
            # Otherwise, simulate a regular game
            winner = sim_game(server, scoring, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,
              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win)
            if winner == 'p1':
                p1_games += 1
            else:
                p2_games += 1
        
        # Check win condition for the set
        if max(p1_games, p2_games) >= 6 and abs(p1_games - p2_games) >= 2:
            break
        
        # Alternate the server after each game
        server = 'p1' if server == 'p2' else 'p2'
    
    # Return the winner of the set
    set_winner = 'p1' if p1_games > p2_games else 'p2'
    
    # Return the winner of the set and the game score
    return set_winner, (p1_games, p2_games)
# Define sim_match function
def sim_match(best_of, surface, scoring, p1, p2):
    # Retrieve player data based on surface
    p1_data = df[(df['name'] == p1) & (df['surface'] == surface)]
    p2_data = df[(df['name'] == p2) & (df['surface'] == surface)]
    # Extract serve and return statistics for both players
    p1_fs_in = p1_data['fs_in_pct'].values[0]
    p1_fs_win = p1_data['fs_win_pct'].values[0]
    p1_ss_in = p1_data['ss_in_pct'].values[0]
    p1_ss_win = p1_data['ss_win_pct'].values[0]
    p1_fr_win = p1_data['fr_win_pct'].values[0]
    p1_sr_win = p1_data['sr_win_pct'].values[0]
    p2_fs_in = p2_data['fs_in_pct'].values[0]
    p2_fs_win = p2_data['fs_win_pct'].values[0]
    p2_ss_in = p2_data['ss_in_pct'].values[0]
    p2_ss_win = p2_data['ss_win_pct'].values[0]
    p2_fr_win = p2_data['fr_win_pct'].values[0]
    p2_sr_win = p2_data['sr_win_pct'].values[0]
    
    # Initialize variables to track sets won by each player
    p1_sets_won = 0
    p2_sets_won = 0
    
    # Initialize variable to track the number of games played in previous sets
    total_games_played = 0
    
    # Loop to simulate best-of-n set sequence
    while p1_sets_won < (best_of + 1) // 2 and p2_sets_won < (best_of + 1) // 2:
        # Determine the initial server for the set based on the total number of games played
        # If odd - p2 is the first server in the set
        # Initialize the server as player 1
        initial_server = "p1" if total_games_played % 2 == 0 else "p2"
        
        # Simulate one set
        set_winner, game_score = sim_set(scoring, initial_server, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,
              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win)
        
        # Update the number of games played in previous sets
        total_games_played += sum(game_score)
        
        # Aggregate set results
        if set_winner == 'p1':
            p1_sets_won += 1
        else:
            p2_sets_won += 1
    
    # Return the aggregate set results
    return (p1_sets_won, p2_sets_won)
# Test the simulation for a match
def run_simulations(simulations, best_of, surface, scoring, p1, p2):
    results = [] # Create empty data frame
    for _ in range(simulations):
        results.append(sim_match(best_of, surface, scoring, p1, p2))
    return results
# ATP interact
atp = df[df['league'] == "ATP"] # Filter out WTA data
atp_names = atp['name'].drop_duplicates() # Get unique player names
@interact_manual(
    # Create inputs for number of simulations, best of n sets, surface, scoring type, and player
    simulations=[1, 10, 50, 100, 500, 1000, 5000, 10000], 
    best_of=[3, 5],
    surface=['Hard', 'Clay', 'Grass'],
    scoring=['ad', 'no-ad'],
    p1=[""] + list(atp_names),
    p2=[""] + list(atp_names))
def get_inputs(simulations, best_of, surface, scoring, p1, p2):
    # Use try and except to account for errors in player sample size
    try:
        # Run simulations
        sims = run_simulations(simulations, best_of, surface, scoring, p1, p2)
        counter = (Counter(sims))
        most_common = max(counter.items(), key=lambda x: x[1])[0]
        x = most_common[0]
        y = most_common[1]
        # Aggregate sim results
        sims = pd.DataFrame(sims, columns=['p1_sets', 'p2_sets'])
        p1_sets = sims['p1_sets'].sum()
        p2_sets = sims['p2_sets'].sum()
        p1_x_sets = round(p1_sets/len(sims), 2)
        p2_x_sets = round(p2_sets/len(sims), 2)
        # Calculate total matches won by each player
        p1_win_prob = round((((sims['p1_sets'] > sims['p2_sets'])).sum()/len(sims)) * 100)
        print(f"The most common result is {p1} ({x}) - {p2} ({y})")
        print(f"The expected match result is {p1} ({p1_x_sets}) - {p2} ({p2_x_sets})")
        if (p1_win_prob < 50):
            print(f"{p2} wins {100 - p1_win_prob}% of the time.")
        else:
            print(f"{p1} wins {p1_win_prob}% of the time.")
    except:
        print("At least one player has not played at least 1000 service points on the surface selected.")
# interact - wta
wta = df[df['league'] == "WTA"]
wta_names = wta['name'].drop_duplicates()
@interact_manual(
    simulations=[1, 10, 50, 100, 500, 1000, 5000, 10000], 
    best_of=[3, 5],
    surface=['Hard', 'Clay', 'Grass'],
    scoring=['ad', 'no-ad'],
    p1=[""] + list(wta_names),
    p2=[""] + list(wta_names))
def get_inputs(simulations, best_of, surface, scoring, p1, p2):
    try:
        # Run simulations
        sims = run_simulations(simulations, best_of, surface, scoring, p1, p2)
        counter = (Counter(sims))
        most_common = max(counter.items(), key=lambda x: x[1])[0]
        x = most_common[0]
        y = most_common[1]
        # Aggregate sim results
        sims = pd.DataFrame(sims, columns=['p1_sets', 'p2_sets'])
        p1_sets = sims['p1_sets'].sum()
        p2_sets = sims['p2_sets'].sum()
        p1_x_sets = round(p1_sets/len(sims), 2)
        p2_x_sets = round(p2_sets/len(sims), 2)
        # Calculate total matches won by each player
        p1_win_prob = round((((sims['p1_sets'] > sims['p2_sets'])).sum()/len(sims)) * 100)
        print(f"The most common result is {p1} ({x}) - {p2} ({y})")
        print(f"The expected match result is {p1} ({p1_x_sets}) - {p2} ({p2_x_sets})")
        if (p1_win_prob < 50):
            print(f"{p2} wins {100 - p1_win_prob}% of the time.")
        else:
            print(f"{p1} wins {p1_win_prob}% of the time.")
    except:
        print("At least one player has not played at least 1000 service points on the surface selected.")
atp_names.reset_index(drop=True, inplace=True)
wta_names.reset_index(drop=True, inplace=True)
random.seed(12345)
atp_data = []
for _ in range(1000000):  # Create list of 1 million matchups
    # Create weights for random matchups choices
    best_of = random.choices([3, 5], weights=[0.6, 0.4])[0]
    surface = random.choices(['Hard', 'Clay', 'Grass'], weights=[.56, .33, .11])[0]
    scoring = random.choices(['ad', 'no-ad'], weights=[.8, .2])[0]
    atp_names_list = list(atp_names)  # Convert atp_names to a list
    p1 = random.choice(atp_names_list)
    p2 = random.choice([name for name in atp_names_list if name != p1])
    atp_data.append([best_of, surface, scoring, p1, p2])

# Create DataFrame
atp_df = pd.DataFrame(atp_data, columns=['best_of', 'surface', 'scoring', 'p1', 'p2'])
# Remove any ATP matches in which players have insufficient matches on that surface
rm_obs = atp[['name', 'surface', 'svpt']]
newdf = pd.merge(atp_df, rm_obs, left_on = ['p1', 'surface'], right_on = ['name', 'surface'], how = 'left')
newdf = pd.merge(newdf, rm_obs, left_on = ['p2', 'surface'], right_on = ['name', 'surface'], how = 'left')
atp_matchups = newdf.dropna()
random.seed(12345)
wta_data = []
for _ in range(1000000):  # Create 1 million matchups
    # Create weights for random matchups choices
    best_of = random.choices([3, 5], weights=[0.6, 0.4])[0]
    surface = random.choices(['Hard', 'Clay', 'Grass'], weights=[.56, .33, .11])[0]
    scoring = random.choices(['ad', 'no-ad'], weights=[.8, .2])[0]
    wta_names_list = list(wta_names)  # Convert atp_names to a list
    p1 = random.choice(wta_names_list)
    p2 = random.choice([name for name in wta_names_list if name != p1])
    wta_data.append([best_of, surface, scoring, p1, p2])

# Create DataFrame
wta_df = pd.DataFrame(wta_data, columns=['best_of', 'surface', 'scoring', 'p1', 'p2'])
# Remove any ATP matches in which players have insufficient matches on that surface
rm_obs2 = wta[['name', 'surface', 'svpt']]
newdf2 = pd.merge(wta_df, rm_obs2, left_on = ['p1', 'surface'], right_on = ['name', 'surface'], how = 'left')
newdf2 = pd.merge(newdf2, rm_obs2, left_on = ['p2', 'surface'], right_on = ['name', 'surface'], how = 'left')
wta_matchups = newdf2.dropna()
# Bind rows for all ATP/WTA matchups
matchups = pd.concat([atp_matchups, wta_matchups])
matchup_preds = matchups[['best_of', 'surface', 'scoring', 'p1', 'p2']]
# Function to predict match results for each row in the DataFrame
def predict_match_results(row, sim_number):
    # Extract information from the DataFrame row
    best_of = row['best_of']
    surface = row['surface']
    scoring = row['scoring']
    p1 = row['p1']
    p2 = row['p2']
    
    # Predict match results using simulate_match function
    p1_sets_won, p2_sets_won = sim_match(best_of, surface, scoring, p1, p2)
    
    # Print out the sim number
    print(f"Simulation {sim_number}: {p1} vs {p2} - Sets won: {p1_sets_won} vs {p2_sets_won}, {surface}, {scoring}")

    # Return the predicted match results
    return pd.DataFrame({'Simulation': sim_number, 'Player 1': p1, 'Player 2': p2, 'Scoring': scoring, 'Surface': surface, 'Sets won by Player 1': p1_sets_won, 'Sets won by Player 2': p2_sets_won}, index=[0])
# Apply the predict_match_results function to each row of the DataFrame
results = matchup_preds.apply(lambda row: predict_match_results(row, row.name + 1), axis=1)
# Concatenate the DataFrames
results = pd.concat(results.tolist(), ignore_index=True)
# Create best of columns for ATP/WTA observations
results.loc[0:522895, 'Best of'] = 5
results.loc[522896:1055803, 'Best of'] = 3
# Select columns from results, and add in a column for scoring and simulations
sim_100 = results[['Simulation', "Player 1", "Player 2", 'Surface', 'Best of']]
sim_100['Scoring'] = "ad"
sim_100['Simulations'] = 100
storage_df = sim_100
sim_100 = sim_100[['Player 1', 'Player 2', "Surface", "Best of", "Scoring", "Simulations"]]
# Create a function to simulate 100 matches of each row observation from "results"
def predict_sim_100(row):
    # Extract information from the DataFrame row
    simulations = row['Simulations']
    best_of = row['Best of']
    surface = row['Surface']
    scoring = row['Scoring']
    p1 = row['Player 1']
    p2 = row['Player 2']
    
    # Predict match results using simulate_match function
    results = run_simulations(simulations, best_of, surface, scoring, p1, p2)
    
    # Calculate probabilities from the results
    p1_win_prob = (sum(result[0] > result[1] for result in results) / simulations) * 100
    
    print(f"Simulating {simulations} {best_of} set matches for players {p1} vs {p2}...")

    # Return the predicted match results
    return p1_win_prob
# Apply function
sim_res = sim_100.apply(predict_sim_100, axis=1)
#sim_res.to_csv("sim results.csv", index = False)
sim_res = pd.DataFrame(sim_res, columns=['p1 win prob'])
results['p1_win_prob'] = sim_res['p1 win prob']
results.to_csv("All Sim Results.csv", index = False) # Write out a csv to store simulation results
