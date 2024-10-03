{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": []
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "5r2s8QHzOpz8"
      },
      "outputs": [],
      "source": [
        "# Import libraries\n",
        "import pandas as pd\n",
        "import streamlit as st\n",
        "import numpy as np\n",
        "import random\n",
        "from collections import Counter, defaultdict"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "# Create a fcn that reads in the data for a given year\n",
        "def read_data(yr):\n",
        "    atp_data = pd.read_csv(f\"atp_matches_{yr}.csv\")\n",
        "    atp_data['league'] = \"ATP\"\n",
        "    # Select columns from data set\n",
        "    atp_data = atp_data[\n",
        "        ['winner_name', 'loser_name', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_df',\n",
        "         'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_df',\n",
        "         'league', 'surface']]\n",
        "\n",
        "    wta_data = pd.read_csv(f\"wta_matches_{yr}.csv\")\n",
        "    wta_data['league'] = \"WTA\"\n",
        "    wta_data = wta_data[\n",
        "        ['winner_name', 'loser_name', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_df',\n",
        "         'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_df',\n",
        "         'league', 'surface']]\n",
        "\n",
        "    data = pd.concat([atp_data, wta_data])\n",
        "    return data"
      ],
      "metadata": {
        "id": "NcyvgfRlkZEr"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Apply read_data fcn\n",
        "data = read_data(2023)\n",
        "data.dropna(inplace=True) # Remove all NAs"
      ],
      "metadata": {
        "id": "sFwesuUTkz5P"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Split up winners/losers columns\n",
        "winners = data[['winner_name', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_df',\n",
        "                'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_df',\n",
        "                'league', 'surface']]\n",
        "losers = data[['loser_name', 'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon', 'l_df',\n",
        "               'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_df',\n",
        "               'league', 'surface']]"
      ],
      "metadata": {
        "id": "IWFBmu_Sk8GD"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Change colnames for winners/losers to be player/opponent cols\n",
        "winners = winners.rename(columns={\n",
        "    'winner_name': 'name',\n",
        "    'w_svpt': 'svpt',\n",
        "    'w_1stIn': 'fs_in',\n",
        "    'w_1stWon': 'fs_win',\n",
        "    'w_2ndWon': 'ss_win',\n",
        "    'w_df': 'df',\n",
        "    'l_svpt': 'o_svpt',\n",
        "    'l_1stIn': 'o_fs_in',\n",
        "    'l_1stWon': 'o_fs_win',\n",
        "    'l_2ndWon': 'o_ss_win',\n",
        "    'l_df': 'o_df'\n",
        "})\n",
        "losers = losers.rename(columns={\n",
        "    'loser_name': 'name',\n",
        "    'l_svpt': 'svpt',\n",
        "    'l_1stIn': 'fs_in',\n",
        "    'l_1stWon': 'fs_win',\n",
        "    'l_2ndWon': 'ss_win',\n",
        "    'l_df': 'df',\n",
        "    'w_svpt': 'o_svpt',\n",
        "    'w_1stIn': 'o_fs_in',\n",
        "    'w_1stWon': 'o_fs_win',\n",
        "    'w_2ndWon': 'o_ss_win',\n",
        "    'w_df': 'o_df'\n",
        "})"
      ],
      "metadata": {
        "id": "kEDhH_O-k8yR"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Combine winners/losers dfs\n",
        "df = pd.concat([winners, losers])"
      ],
      "metadata": {
        "id": "5pV2O6HPlDeT"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "grouped_data = df.groupby(['name', 'league', 'surface']).sum().reset_index() # Sum over all variables after grouping by name, league and surface\n",
        "grouped_data = grouped_data[grouped_data['svpt'] > 1000] # Filter out < 1000 observations\n",
        "# Calculate player rate stats\n",
        "grouped_data['fs_in_pct'] = grouped_data['fs_in'] / grouped_data['svpt']\n",
        "grouped_data['fs_win_pct'] = grouped_data['fs_win'] / grouped_data['fs_in']\n",
        "grouped_data['ss_in_pct'] = 1 - (grouped_data['df'] / (grouped_data['svpt'] - grouped_data['fs_in']))\n",
        "grouped_data['ss_win_pct'] = grouped_data['ss_win'] / (grouped_data['svpt'] - grouped_data['fs_in'] - grouped_data['df'])\n",
        "grouped_data['fr_win_pct'] = 1 - (grouped_data['o_fs_win'] / grouped_data['o_fs_in'])\n",
        "grouped_data['sr_win_pct'] =  1 - (grouped_data['o_ss_win'] / (grouped_data['o_svpt'] - grouped_data['o_fs_in'] - grouped_data['o_df']))\n",
        "# Create grouped data frame\n",
        "df = grouped_data[['name', 'league', 'surface', 'fs_in_pct', 'fs_win_pct', 'ss_in_pct', 'ss_win_pct', 'fr_win_pct', 'sr_win_pct']]"
      ],
      "metadata": {
        "id": "lmBYGkSTlIKs"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "def loop_point(server_prob, returner_prob):\n",
        "    while True: # While loop to infinitely iterate until the server/return prob are True\n",
        "        # If random uniform value <= server prob, server wins and loop breaks\n",
        "        if (np.random.uniform(low=0, high=1, size = None) <= server_prob):\n",
        "            return('server')\n",
        "            break\n",
        "        elif (np.random.uniform(low=0, high=1, size = None) <= returner_prob):\n",
        "            return('returner')\n",
        "            break"
      ],
      "metadata": {
        "id": "uVscTVL4lqLA"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Accounting for likelihood of a first/second serve being in and the server/returner winning on a first/second serve based on serve in play\n",
        "def sim_point(server,\n",
        "              p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,\n",
        "              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win\n",
        "             ):\n",
        "    if server == 'p1': # If the server is p1, sim point for that server\n",
        "        if (np.random.uniform(low=0, high=1, size = None) <= p1_fs_in): # If first serve is made\n",
        "            res = loop_point(p1_fs_win, p2_fr_win) # Simulate first serve point\n",
        "            if res == 'server': # If point winner is server return 'p1' else return 'p2'\n",
        "                return('p1')\n",
        "            else:\n",
        "                return('p2')\n",
        "                # If second serve is made\n",
        "        elif (np.random.uniform(low=0, high=1, size = None) <= p1_ss_in):\n",
        "            res = loop_point(p1_ss_win, p2_sr_win) # Simulate second serve point\n",
        "            if res == 'server': # If point winner is server return 'p1' else return 'p2'\n",
        "                return('p1')\n",
        "            else:\n",
        "                return('p2')\n",
        "        else:\n",
        "            return('p2')\n",
        "    elif server == 'p2':\n",
        "        if (np.random.uniform(low=0, high=1, size = None) <= p2_fs_in): # If first serve is made\n",
        "            res = loop_point(p2_fs_win, p1_fr_win) # Simulate first serve point\n",
        "            if res == 'server': # If point winner is server return 'p2' else return 'p1'\n",
        "                return('p2')\n",
        "            else:\n",
        "                return('p1')\n",
        "        elif (np.random.uniform(low=0, high=1, size = None) <= p2_ss_in): # If second serve is made\n",
        "            res = loop_point(p2_ss_win, p1_sr_win) # Simulate second serve point\n",
        "            if res == 'server': # If point winner is server return 'p2' else return 'p1'\n",
        "                return('p2')\n",
        "            else:\n",
        "                return('p1')\n",
        "        else:\n",
        "            return('p1')"
      ],
      "metadata": {
        "id": "yeTeYeTSluAb"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Simulate a game\n",
        "def sim_game(server, scoring, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,\n",
        "              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win):\n",
        "    # Initialize scores\n",
        "    p1_score = 0\n",
        "    p2_score = 0\n",
        "    while True: # Iterate a game over multiple points\n",
        "        # Simulate a point\n",
        "        winner = sim_point(server,\n",
        "              p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,\n",
        "              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win\n",
        "             )\n",
        "        if winner == 'p1': # If winner is 'p1'\n",
        "            p1_score += 1 # Increase p1's score + 1\n",
        "        else:\n",
        "            p2_score += 1 # Increase p2's score + 1 (if winner is not 'p1')\n",
        "        if scoring == 'ad': # If playing ad scoring\n",
        "            # One player needs to have at least 4 points and \"win by 2\"\n",
        "            if max(p1_score, p2_score) >= 4 and abs(p1_score - p2_score) >= 2:\n",
        "                break\n",
        "        elif scoring == 'no-ad':\n",
        "            # If no-ad, first to 4 points\n",
        "            if max(p1_score, p2_score) == 4:\n",
        "                break\n",
        "    return 'p1' if p1_score > p2_score else 'p2'\n",
        "    # Once the game has finished, if p1 score > p2 score return 'p1' if not return 'p2'"
      ],
      "metadata": {
        "id": "eWENdCnamOEi"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Simulate the actions of a tiebreak\n",
        "def sim_tb(server, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,\n",
        "              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win):\n",
        "    p1_points = 0\n",
        "    p2_points = 0\n",
        "    current_server = server # Based on first set server - later function input\n",
        "\n",
        "    while True:\n",
        "        # Simulate a point\n",
        "        winner = sim_point(current_server,\n",
        "              p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,\n",
        "              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win\n",
        "             )\n",
        "\n",
        "        # Update scores\n",
        "        if winner == 'p1':\n",
        "            p1_points += 1\n",
        "        else:\n",
        "            p2_points += 1\n",
        "\n",
        "        # Check win condition\n",
        "        if max(p1_points, p2_points) >= 7 and abs(p1_points - p2_points) >= 2:\n",
        "            break\n",
        "\n",
        "        # Alternate server every two points\n",
        "        if (p1_points + p2_points) % 2 != 0:\n",
        "            current_server = 'p1' if current_server == 'p2' else 'p2'\n",
        "\n",
        "    # Return the winner of the tiebreaker\n",
        "    return 'p1' if p1_points > p2_points else 'p2'"
      ],
      "metadata": {
        "id": "WtZq1UVKmopZ"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Simulate an individual set\n",
        "def sim_set(scoring, server, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,\n",
        "              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win):\n",
        "    # Initialize player games\n",
        "    p1_games = 0\n",
        "    p2_games = 0\n",
        "\n",
        "    while True:\n",
        "        # If both players have won 6 games, play a tiebreaker\n",
        "        if p1_games == 6 and p2_games == 6:\n",
        "            winner = sim_tb(server, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,\n",
        "              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win)\n",
        "            if winner == 'p1':\n",
        "                p1_games += 1\n",
        "            else:\n",
        "                p2_games += 1\n",
        "            break\n",
        "        else:\n",
        "            # Otherwise, simulate a regular game\n",
        "            winner = sim_game(server, scoring, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,\n",
        "              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win)\n",
        "            if winner == 'p1':\n",
        "                p1_games += 1\n",
        "            else:\n",
        "                p2_games += 1\n",
        "\n",
        "        # Check win condition for the set\n",
        "        if max(p1_games, p2_games) >= 6 and abs(p1_games - p2_games) >= 2:\n",
        "            break\n",
        "\n",
        "        # Alternate the server after each game\n",
        "        server = 'p1' if server == 'p2' else 'p2'\n",
        "\n",
        "    # Return the winner of the set\n",
        "    set_winner = 'p1' if p1_games > p2_games else 'p2'\n",
        "\n",
        "    # Return the winner of the set and the game score\n",
        "    return set_winner, (p1_games, p2_games)"
      ],
      "metadata": {
        "id": "BpH074okng8A"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Create sim_match function\n",
        "def sim_match(best_of, surface, scoring, p1, p2):\n",
        "    # Retrieve player data based on surface\n",
        "    p1_data = df[(df['name'] == p1) & (df['surface'] == surface)]\n",
        "    p2_data = df[(df['name'] == p2) & (df['surface'] == surface)]\n",
        "    # Extract serve and return statistics for both players\n",
        "    p1_fs_in = p1_data['fs_in_pct'].values[0]\n",
        "    p1_fs_win = p1_data['fs_win_pct'].values[0]\n",
        "    p1_ss_in = p1_data['ss_in_pct'].values[0]\n",
        "    p1_ss_win = p1_data['ss_win_pct'].values[0]\n",
        "    p1_fr_win = p1_data['fr_win_pct'].values[0]\n",
        "    p1_sr_win = p1_data['sr_win_pct'].values[0]\n",
        "    p2_fs_in = p2_data['fs_in_pct'].values[0]\n",
        "    p2_fs_win = p2_data['fs_win_pct'].values[0]\n",
        "    p2_ss_in = p2_data['ss_in_pct'].values[0]\n",
        "    p2_ss_win = p2_data['ss_win_pct'].values[0]\n",
        "    p2_fr_win = p2_data['fr_win_pct'].values[0]\n",
        "    p2_sr_win = p2_data['sr_win_pct'].values[0]\n",
        "\n",
        "    # Initialize variables to track sets won by each player\n",
        "    p1_sets_won = 0\n",
        "    p2_sets_won = 0\n",
        "\n",
        "    # Initialize variable to track the number of games played in previous sets\n",
        "    total_games_played = 0\n",
        "\n",
        "    # Loop to simulate best-of-n set sequence\n",
        "    while p1_sets_won < (best_of + 1) // 2 and p2_sets_won < (best_of + 1) // 2:\n",
        "        # Determine the initial server for the set based on the total number of games played\n",
        "        # If odd - p2 is the first server in the set\n",
        "        # Initialize the server as player 1\n",
        "        initial_server = \"p1\" if total_games_played % 2 == 0 else \"p2\"\n",
        "\n",
        "        # Simulate one set\n",
        "        set_winner, game_score = sim_set(scoring, initial_server, p1_fs_in, p1_fs_win, p1_ss_in, p1_ss_win, p1_fr_win, p1_sr_win,\n",
        "              p2_fs_in, p2_fs_win, p2_ss_in, p2_ss_win, p2_fr_win, p2_sr_win)\n",
        "\n",
        "        # Update the number of games played in previous sets\n",
        "        total_games_played += sum(game_score)\n",
        "\n",
        "        # Aggregate set results\n",
        "        if set_winner == 'p1':\n",
        "            p1_sets_won += 1\n",
        "        else:\n",
        "            p2_sets_won += 1\n",
        "\n",
        "    # Return the aggregate set results\n",
        "    return (p1_sets_won, p2_sets_won)"
      ],
      "metadata": {
        "id": "1opAm3x8nzx1"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "def run_simulations(simulations, best_of, surface, scoring, p1, p2):\n",
        "    results = [] # Create empty data frame\n",
        "    for _ in range(simulations): # Loop through n simulations\n",
        "    # Run a match sim and append to \"results\" for each iteration\n",
        "        results.append(sim_match(best_of, surface, scoring, p1, p2))\n",
        "    return results"
      ],
      "metadata": {
        "id": "MYlNvwpcn4zn"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Get player names for ATP/WTA\n",
        "# Filter players based on ATP or WTA\n",
        "def filter_players(df, league):\n",
        "    filtered_df = df[df['league'] == league]\n",
        "    return filtered_df['name'].drop_duplicates()"
      ],
      "metadata": {
        "id": "uMucEAQ0oXtG"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "### Create streamlit\n",
        "# Input for ATP/WTA selection\n",
        "league = st.sidebar.radio(\"Select League\", (\"ATP\", \"WTA\"))\n",
        "# Filter player names based on selected league\n",
        "if league == \"ATP\":\n",
        "    player_names = filter_players(df, \"ATP\")\n",
        "else:\n",
        "    player_names = filter_players(df, \"WTA\")"
      ],
      "metadata": {
        "id": "xsHqy08IoePm"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "# Streamlit inputs & UI\n",
        "st.sidebar.header(\"Simple Match Simulations\")\n",
        "simulations = st.sidebar.selectbox(\"Number of simulations\", [1, 10, 50, 100, 500, 1000, 5000, 10000])\n",
        "best_of = st.sidebar.selectbox(\"Best of\", [3, 5])\n",
        "surface = st.sidebar.selectbox(\"Surface\", ['Hard', 'Clay', 'Grass'])\n",
        "scoring = st.sidebar.selectbox(\"Scoring\", ['ad', 'no-ad'])\n",
        "p1 = st.sidebar.selectbox(\"Player 1\", [\"\"] + list(player_names))\n",
        "p2 = st.sidebar.selectbox(\"Player 2\", [\"\"] + list(player_names))"
      ],
      "metadata": {
        "id": "0uveEoCloiin"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "if st.sidebar.button(\"Simulate Match\"):\n",
        "    if p1 and p2: # If there exists a p1 and p2\n",
        "        try: # Run try/except to handle possible errors\n",
        "            # Run simulations\n",
        "            sims = run_simulations(simulations, best_of, surface, scoring, p1, p2)\n",
        "            counter = (Counter(sims)) # Count n sims\n",
        "            most_common = max(counter.items(), key=lambda x: x[1])[0] # Find the most frequent match outcome\n",
        "            # Pull the most common set score for x (p1) and y (p2)\n",
        "            x = most_common[0]\n",
        "            y = most_common[1]\n",
        "            # Aggregate sim results\n",
        "            sims = pd.DataFrame(sims, columns=['p1_sets', 'p2_sets'])\n",
        "            p1_sets = sims['p1_sets'].sum()\n",
        "            p2_sets = sims['p2_sets'].sum()\n",
        "            p1_x_sets = round(p1_sets/len(sims), 2)\n",
        "            p2_x_sets = round(p2_sets/len(sims), 2)\n",
        "            # Calculate total matches won by each player\n",
        "            p1_win_prob = round((((sims['p1_sets'] > sims['p2_sets'])).sum()/len(sims)) * 100)\n",
        "            # Write most common match result, and expected match result\n",
        "            st.write(f\"The most common result is: {p1} ({x}) - {p2} ({y})\")\n",
        "            st.write(f\"The expected match result is: {p1} ({p1_x_sets}) - {p2} ({p2_x_sets})\")\n",
        "            if (p1_win_prob < 50): # If p1 win probability < 50 display p2 win probability\n",
        "                st.write(f\"{p2} wins {100 - p1_win_prob}% of the time.\")\n",
        "            else: # If not display p1 win probability\n",
        "                st.write(f\"{p1} wins {p1_win_prob}% of the time.\")\n",
        "        except: # If there is an error, write this message\n",
        "            st.write(\"At least one player has not played at least 1000 service points on the surface selected.\")\n",
        "st.title(\"Tennis Match Simulator (Based on 2023 Performance Data)\") # Add a title"
      ],
      "metadata": {
        "id": "43GcNX7lonsb"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}
