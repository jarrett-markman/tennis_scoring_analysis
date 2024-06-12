# Analyzing Tennis Scoring

# Check out the simulation tool for this project [here](https://simple-tennis-simulation.streamlit.app/)!

With this simulation tool you can simulate a given ATP or WTA match with the following parameters:
- Number of simulations (1, 10, 100, 500, 1000, 5000, 10000).
- Best of 3 or 5 sets.
- Surface (Hard, Clay, Grass - though some players have insufficient sample sizes).
- Scoring (If the matches are played with ad scoring or no-ad scoring).
- Player 1 and Player 2 - select the players to simulate matches with.

## Abstract

**Why have the proclaimed "Big 3" been so dominant?**

For Novak Djokovic, Rafael Nadal, and Roger Federer, their main calling card is their prowess in Grand Slams. While they have all found a lot of success on the ATP tour, all with $>90$ ATP titles, their main claim to dominance is their Grand Slam wins. How could it not be? On the biggest stage, against the best players of the world, they have proven their dominance. This "dominance" is due to the fact that they are the greatest players of their generation. However, in addition to being great players, the best of five scoring system has greatly benefited all three of them.

-   In the 2023 U.S. Open (Currently his last Grand Slam), Novak Djokovic would have lost in the third round to Laslo Djere - $(4-6, 4-6)$.
-   In the 2011 French Open, Rafael Nadal would have lost in the first round to John Isner - $(6-4, 6-7, 6-7)$.
-   In the 2009 French Open, Roger Federer would have lost in the fourth round to Tommy Haas - $(6-7, 5-7)$.

However, they would all go on win these matches in five sets. There are many reasons for this:

-   It is much harder to sustain a level to win three out of five sets.
-   A great player is more likely to positively regress to the mean.
-   A worse player is more likely to negatively regress to the mean.

While there are many other variables to consider in any match (especially a best of five set match), such as timing, fitness, mentality, feeling, and ultimately skill, a large reason for the big 3's success on the grand slam level is that they played 5 sets instead of 3. The Law of Large Numbers says that if you take samples of larger and larger size from any population, then the mean of the sampling distribution, $\mu x$ tends to get closer and closer to the true population mean, $\mu$. The Law of Large Numbers can be applied to these 3 players finding so much success in the best of five scoring system. Because the sample is larger, the true distribution in grand slams is much more clear than in other tournaments (ATP 250s, 500s, Masters 1000s).

How can we measure the effects of different scoring systems in professional tennis? How does deuce-ad and set scoring benefit certain players?

## Methodology

### First-Step Analysis

We can solve the probability of a server and a returner winning a deuce game using a Stochastic Process called **First-Step Analysis**.

A **Markov Chain** is a stochastic model that describes a sequence of possible events in which the probability of each event is based on only the previous state within the chain.

**First-Step Analysis** is a specific Markov process that can measure the likelihood of transitioning to each state within a Markov chain.

For this **Markov chain** we have the following state space:

$$\mathbb{S} = \{Deuce,\ Advantage\ Server,\ Advantage\ Returner,\ Game\ Server,\ Game\ Returner\}$$

To calculate the probability of a server or a returner winning a deuce game we can apply **First-Step Analysis** with the function:

$$f(x) = P[Server\ Wins\ Deuce\ Game\ |\ X(0) = x]\ for\ all\ x\ in\ \mathbb{S}$$

In order to calculate the probability of a single point the following assumptions will be made:

-   Each point is i.i.d (independent and identically distributed)
-   The past does not matter (how the game got to deuce)
-   Player performance is independent of pressure
-   Player ability is independent of pressure and other possible effects
-   The possible outcomes for winning an individual point are:
    -   $\mathbb{S} = \{Server,\ Returner\}$
    -   $P[Server\ Wins\ a\ Point] = x\ in[0, 1]$
    -   $P[Returner\ Wins\ a\ Point] = 1 - P[Server\ Wins\ a\ Point]$
    -   $\sum_{}\mathbb{S} = 1$

### In the [**tree diagram**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/Tree%20Diagram.png) we can visualize this **Markov Chain**.

Where x represents the likelihood of the server winning a point and 1 - x represents the likelihood of the returner winning a point.

As previously stated, **First-Step Analysis** is a specific Markov process that can measure the likelihood of transitioning to each state within a Markov chain.

With this we can solve the probability of a player winning a game by applying **First-Step Analysis** and **f(x)**.

#### Note the following absorbing states:

$$f(Game\ Server) = 1$$ $$f(Game\ Returner) = 0$$

**We are interested in calculating the probability of the server winning**.

We can calculate the likelihood of transferring between states of the Markov chain.

$$f(Deuce) = xf(Advantage\ Server)\ +\ (1-x)f(Advantage\ Returner)$$ $$f(Advantage\ Server) = (1-x)f(Deuce)\ +\ xf(Game\ Server)$$ $$f(Advantage\ Returner) = xf(Deuce)\ +\ (1-x)f(Game\ Returner)$$ We can create a transition matrix with:

$$\mathbb{S} = \{Deuce,\ Advantage\ Server,\ Advantage\ Returner,\ Game\ Server,\ Game\ Returner\}$$

in that order.

$$\begin{bmatrix}
0 & x & 1-x & 0 & 0\\
1-x & 0 & 0 & x & 0\\
x & 0 & 0 & 0 & 1-x\\
0 & 0 & 0 & 1 & 0\\
0 & 0 & 0 & 0 & 1
\end{bmatrix}$$

**More importantly**, we can calculate the probability of both players winning a game for any point win probability with the following system of equations:

$$\begin{array}{lcl} f(Deuce)-xf(Advantage\ Server) - (1-x)f(Advantage\ Returner)=0\\ 
f(Advantage\ Server) - (1-x)f(Deuce)= x \\
f(Advantage\ Returner) - xf(Deuce)=0 \end{array}$$

### We can visualize the [results](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/Game%20WP%20by%20Scoring.png) of the system of equations for the probability of winning one deuce point, and the probability of winning a game with deuce-ad scoring given the point win probability of "x" for the server.

## Simulation Process

With the power of computing and player performance data from [**Jeff Sackmann**](https://github.com/JeffSackmann), we can create a basic simulation for tennis matches accounting for 3 or 5 set matches, and incorporate a one point deuce,

**The simulation I have created takes into account:**

-   Both players on the court.
-   The surface.
-   The number of sets played.
-   The type of scoring system (deuce-ad versus one deuce point).
-   The probability a serve is made.
-   The probability the server wins the point.
-   The probability the returner wins the point.
-   After a serve is made, each point is "simulated" with a while loop that iterates until the server or returner probability returns **True** (wins the point).

**Additionally, this simulation assumes:**

-   Each point is i.i.d (independent, identically, distributed).
-   Player ability is independent of pressure.
-   Player distribution is approximately normal if they have $>= 1000$ service points.
-   All matches played are based on the players true serve/return ability.
-   Player opponents do not affect player ability
-   All surfaces are independent of each tournament they are played on (e.g. U.S. Open hard court versus Australian Open hard court is negligible).
-   Player ability is independent of different factors such as mental and physical state on each point.

After creating a match simulation, the next step was to generate a list of $1,000,000$ men's and $1,000,000$ women's matches with randomly selected inputs (player, scoring, number of sets, and surface). Players were chosen randomly from a data frame containing all player statistics. Scoring was split $80/20$, the number of sets was split $60/40$, and surface types were split $56/33/11$ to accurately represent the overall ATP season. In addition to predicting $2,000,000$ total individual matches, I decided to additionally simulate all matches 100 times with the same conditions as a grand slam (deuce-ad scoring, best of 3/5 for women/men), to have some measure for the expected winner.

# Results

- [Figure 1 - Tree diagram for deuce-ad scoring](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/Tree%20Diagram.png)
-   [Figure 2 - Game win probability plot for service game win percentage for a server in a deuce game](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/Game%20WP%20by%20Scoring.png))
-   [Figure 3 - Simulation "accuracy" by scoring system](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/Accuracy%20by%20Scoring%20System.png)
-   [Figure 4 - WTA boxplot by scoring system](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/WTA%20Boxplot.png)
-   [Figure 5 - ATP boxplot by scoring system](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/ATP%20Boxplot.png)
-   [Figure 6 - WTA barplot of variance by scoring system](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/ATP%20Variance%20Bar%20Chart.png)
-   [Figure 7 - ATP barplot of variance by scoring system](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/ATP%20Variance%20Bar%20Chart.png)
-   [Figure 8 - Top 20 WTA players](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/WTA%20Table.png)
-   [Figure 9 - Top 20 ATP players](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/ATP%20Table.png)

# References 

All player performance data is sourced from [**Jeff Sackmann's GitHub**](https://github.com/JeffSackmann).
