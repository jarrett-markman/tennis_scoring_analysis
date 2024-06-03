# Analyzing Tennis Scoring

## Abstract

**Why have the proclaimed "Big 3" been so dominant?**

For Novak Djokovic, Rafael Nadal, and Roger Federer, their main calling card is their prowess in Grand Slams. While they have all found a lot of success on the ATP tour, all with >90 ATP titles, their main claim to dominance is their Grand Slam wins. How could it not be? On the biggest stage, against the best players of the world, they have proven their dominance. This "dominance" is due to the fact that they are the greatest players of their generation. However, in addition to being great players, the best of five scoring system has greatly benefitted all three of them. 

- In the 2023 U.S. Open (Currently his last Grand Slame), Novak Djokovic would have lost in the third round to Laslo Djere - 4-6, 4-6. 
- In the 2011 French Open, Rafael Nadal would have lost in the first round to John Isner - 6-4, 6-7, 6-7.
- In the 2009 French Open, Roger Federer would have lost in the fourth round to Tommy Haas - 6-7(4), 5-7.

However, they would all go on win these matches in 5 sets. There are many reasons for this. 
- It is much harder to sustain a level to beat one of the big 3 for at least 3 sets.
- On an "off day" there is more time for the better player to reach their highest level.

While there are many other variables to consider in any match (especially a best of five set match), such as timing, fitness, mentality, feeling, and ultimately skill, a large reason for the big 3's success on the grand slam level is that they played 5 sets instead of 3. The Law of Large Numbers says that if you take samples of larger and larger size from any population, then the mean of the sampling distribution, $\mu x$ tends to get closer and closer to the true population mean, $\mu$. The Law of Large Numbers can be applied to these 3 players finding so much success in the best of 5 scoring system. Because the sample is larger, the true distribution in grand slams is much more clear than in other tournaments (ATP 250s, 500s, Masters 1000s). 

How can we measure the effects of different scoring systems in professional tennis? How does deuce-ad and set scoring benefit certain players?

## Methodology

### First-Step Analysis

We can solve the probability of a server and a returner winning a deuce game using a Stochastic Process called **First-Step Analysis**. 

A **Markov Chain** is a stochastic model that describes a sequence of possible events in which the probability of each event is based on only the previous state within the chain. 

**First-Step Analysis** is a specific Markov process that can measure the likelihood of transitioning to each state within a Markov chain. 

For this **Markov chain** we have the following state space:

$$\mathbb{S} = \{Deuce,\ Advantage\ Server,\ Advantage\ Returner,\ Game\ Server,\ Game\ Returner\}$$

To calculate the probability of a server (or a returner) winning a deuce game we can apply **First-Step Analysis** with the function:

$f(x) = P[Server\ Wins\ Deuce\ Game \|\ X(0) = x]\ for\ all\ x\ i.i.d.\ (independent\ and\ identically\ distributed) \in\ \mathbb{S}$

In order to calculate the probability of a single point the following assumptions will be made:

* Each point is i.i.d (independent and identically distributed)
* The past does not matter (how the game got to deuce)
* Player performance is independent of pressure
* Player ability is independent of pressure and other possible effects
* The possible outcomes for winning an individual point are: 

$\mathbb{S} = \{Server,\ Returner\}$

#### Note the following absorbing states:

$f(Game\ Server) = 1$

$f(Game\ Returner) = 0$

**We are interested in calculating the probability of the server winning**.

We can calculate the likelihood of transferring between states of the Markov chain.

$$f(Deuce) = xf(Advantage\ Server)\ +\ (1-x)f(Advantage\ Returner)$$
$$f(Advantage\ Server) = (1-x)f(Deuce)\ +\ xf(Game\ Server)$$
$$f(Advantage\ Returner) = xf(Deuce)\ +\ (1-x)f(Game\ Returner)$$
We can create a transition matrix with:

$$\mathbb{S} = \{Deuce,\  Advantage\ Server,\  Advantage\ Returner,\  Game\ Server,\  Game\ Returner\}$$ 

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

[Click here to visualize this process](fs_analysis.pdf)

[Click here to view results](ggplot.pdf)

### Simulating matches

With the power of computing and player performance data from [Jeff Sackmann](https://github.com/JeffSackmann), we can create a basic simulation for tennis matches accounting for 3 or 5 set matches, as well as ad versus no-ad scoring. 

[Sim code here](sim_code.py)

**The sim I have created takes into account:**
- The probability a serve is made.
- The probability the server wins the point.
- The probability the returner wins the point.
- After a serve is made, each point is "simulated" with a while loop that iterates until the server or returner probability returns **true** (wins the point). 

**Additionally, this simulation assumes:**
- Each point is i.i.d (independent, identically, distributed)
- Player ability is independent of pressure
- Player distribution is approximately normal if they have $>= 1000$ service points
- All matchups played are appx. normal
- All surfaces are independent of each tournament they are played on (e.g. U.S. Open Hard Court versus Australian Open Hard Court is negligible)
- Player ability is independent of "form"

## Results
