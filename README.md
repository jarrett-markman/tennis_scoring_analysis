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

Following the simulation, the results revealed several key findings. [**Figure 3**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/Accuracy%20by%20Scoring%20System.png) displays simulation "accuracy" by scoring system. An **accurate** match is defined as a match in which a single simulated match returns the same winner that wins at a higher frequency in 100 grand slam conditioned matches. While there isn't a significantly more accurate scoring system, it's compelling to see that no-ad scoring appears to be more "accurate" than ad scoring. Unsurprisingly, 5 set matches are more accurate than 3 set matches.

We can additionally measure the affects in variance by aggregating player results in terms of their expected match win percentage (average grand slam match win percentage) and measure the difference of their empirical match win percentage (win percentage based on all matches). In [**figure 4**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/WTA%20Boxplot.png) and [**figure 5**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/ATP%20Boxplot.png) we can see boxplots in women's and men's matches. While [**figure 3**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/Accuracy%20by%20Scoring%20System.png) displays no-ad scoring as more accurate, deuce-ad scoring limits variance in both women's and men's tennis, for 3 and 5 sets respectively. The variance is much higher in all scoring systems not true to the same situations as grand slams, and the difference in expected versus actual win percentage in matches is much less variant in 3-set (ad) matches for women, and 5-set (ad) matches for men. This is largely due to two factors. On the men's side, it's unsurprising to see that variance is limited in 5-set and deuce-ad scoring, because the security of another set to win, and a scoring system that favors all of their service games. However, it is surprising that in all women's matches, variance is minimized in best of 3, deuce-ad scoring matches, as the more sets the players play, should favor the "better" player. Additionally, being that given grand slam matches are defined as 3-set and 5-set, deuce-ad scoring matches, over a large sample of $1,000,000$ matches, variance should be limited in the matches that replicate the same conditions, which is why matches appear to be less more variant in the same scoring systems as grand slams.

In [**figure 6**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/WTA%20Variance%20Bar%20Chart.png) and [**figure 7**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/ATP%20Variance%20Bar%20Chart.png), we can see bar charts that display the variance for women's and men's tennis by scoring system. This additionally contributes to the analysis that variance appears to be minimized in grand slam conditions. It is interesting to see that in both women's and men's matches, variance is at its highest in best of five, no-ad scoring matches. It's possible that given the match is longer, and the "better" player in service games (assuming that a player has $>\.62$ win probability on a given service point) loses service games more frequently meaning that service games are much harder to win, so breaks of service will be much more common.

The tables in [**Figure 8**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/WTA%20Table.png) and [**figure 9**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/ATP%20Table.png) display the top women's and men's players in terms of their overall win percentage in all of their matches. You can additionally see their total number of matches, and win probability by each scoring system.

One of the most compelling things that can be seen is that in both tables, these "top players" (deemed so by their simulated results) have **much more success in 5-set matches**. This is due in part to the fact that because they are statistically so strong, it is much harder for their opponents to win 3 sets before they win 3 sets, whereas it's easier for their opponents to sustain a high level to win 2 sets before they win 2 sets.

The simulation itself appears to be accurate in predicting success as the top two women's players are Iga Swiatek and Aryna Sabalenka, and the top three men's players are Novak Djokovic, Jannik Sinner, and Carlos Alcaraz. While the top of the list indicates some of the best players, it is additionally important to notice that the simulation favors a lot of big servers in the ATP, that have not had that much success on the ATP. Players like Borna Gojo, Jack Draper, and John Isner are all highly skilled servers, but their return has held them back from finding more success. This can indicate that having a good serve is very predictive in future success, and they may be able to find success in the future. This is not limited to high-level servers, as players like Gojo, Draper, Yulia Putintseva, Leylah Fernandez, and Thanasi Kokkinakis may all be due for success at certain tournaments in the future. Their expected success can also be shown in the fact that someone like Leylah Fernandez has shown she can reach the final of a high-level tournament (2021 U.S. Open).

Additionally, it appears that no-ad scoring benefits certain players, whereas ad scoring benefits other players. High level servers and returners (Swiatek, Djokovic, Sinner, Alcaraz) tend to perform better in no-ad scoring, whereas many different players performance in no-ad or ad scoring is more variant.

The reason for each players success based on a scoring system is variant for almost any player. Someone like John Isner has a higher win percentage in no-ad scoring than in ad scoring, despite the much higher likelihood of losing a service game in no-ad scoring. While that phenomenon is true, because he has such a dominant serve, he will still win a majority of his service games, and not be majorly affected by no-ad scoring. Where this benefits him however, is that because breaks of serve are so hard to come by, he wins much more return games with no-ad scoring. Overall, no-ad scoring ends up being more favorable to him because the benefit of winning more games with his relatively "weak" return outweights the drawback of losing service games in no-ad scoring. In layman's terms, he wins more return games than he loses service games.

This same idea can be applied similarly to other high level servers that excel at serving in the WTA like Elena Rybakina, and Caroline Garcia. However, because breaks of serve are more common in the WTA, no-ad scoring benefits them because they are dominant on serve and not highly effective on return. Like with Isner, no-ad scoring lets them win more return games than they lose service games.

Aryna Sabalenka and Madison Keys fit a similar mold as Rybakina and Garcia, however, because they are better on return, 5-set ad scoring is more beneficial to them. The security of an ad-service game means they will hold serve frequently, however, because they are somewhat successful on return, no-ad scoring will not benefit them to break serve more than they will fail to hold serve.

In the ATP, Stefanos Tsitsipas replicates this idea. While he is a highly effective server, because he are good enough on return to break serve frequently enough, the security of ad scoring helps him hold serve more, whereas no-ad scoring would lead to less service games won, and despite winning more return games with no-ad scoring, he will win more service games than lose return games with ad scoring. John Isner doesn't fit this criteria because he isn't good enough on return. Because his return is so weak, no-ad scoring lets him break serve much more often. In the case of Tsitsipas, he is good enough on return that he will already break serve enough with ad scoring.

No-ad scoring benefits players like Iga Swiatek, Jessica Pegula, Novak Djokovic, Jannik Sinner, Carlos Alcaraz, and Taylor Fritz. Why is this the case? This isn't as clear as for the previous players referenced, because all five of these players are successful on both their serve and their return. This is most likely attributable to the fact that because they are effective both on serve and on return, their opponents won't be able to easily break serve, and because of the benefits of no-ad scoring, on return they will be able to win more return games.

# Conclusion & Potential Improvements 

Unsurprisingly, it is very clear that over 5-set matches significantly favor the "better" players. In figures [**8**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/WTA%20Table.png) and [**9**](https://github.com/jarrett-markman/tennis_scoring_analysis/blob/main/viz/ATP%20Table.png), the top 20 women's and men's players have higher win percentages in 5-set matches than in 3-set matches. While the greater number of sets indicate that the "better" player wins more often, I was surprised to see that no-ad scoring favors a lot of high level players, including Iga Swiatek and Novak Djokovic, who held the world number 1 ranking for a majority of the year. In the future, it would be extremely intriguing to examine how scoring can affect serve and return statistics.

Many of the results can be explained based on how the simulation was created. Through pairing an "accuracy" measure between one scoring system, with the "accurate" scoring system being one of the systems, results will be more compelling to that specific scoring system. In this case, because 100 grand slam matches measured "accuracy," variance theoretically should be minimized in those same exact scenarios. Additionally, over a large enough sample, the simulated results by system should align most siimilarly to the criteria being set - in this case 1 match being compared to the results of 100.

Additionally, the simulation definitely tends to favor big servers, as players like Borna Gojo, Jack Draper, John Isner, and Thanasi Kokkinakis were all in the top 20 in terms of win percentage, however, they didn't find that much success on the court. However, it does indicate that players like them are highly capable of beating any player on tour because of how effective their serve is.

While taking into account the ability of the server and returner using the likelihood of a serve being made and a point being won can be an effective way of simulating a tennis match, there are definitely a variety of other factors that significantly contribute to player performance in matches. This simulation does not take into account shot speeds or spin rates, in addition to the varying momentum shifts (albeit impossible to quantify) and mental factors that influence how a player performs. Additionally, the best of five set scoring system tends to favor players with more stamina, whereas the simulation doesn't differentiate between set 1 and set 5.

Furthermore, most of the simulated matches were hard court, ad-scoring, 3 set matches, so it is extremely possible that all simulated matches don't represent true player ability by scoring system. Given that $80\%$ of matches simulated were based on traditional tennis scoring, it's possible that the lack of no-ad matches may indicate that no-ad results may be noisy, and not representative of how it can affect tennis scoring. Additionally, given that almost three out of every five matches were on a hard court, the overall results tend to favor players who perform better on hard courts. This is why someone like Taylor Fritz has a higher overall simulated win percentage than Stefanos Tsitsipas: Fritz is a highly effective player on hard courts, whereas Tsitsipas is highly effective on clay.

In the future, it would be interesting to examine how scoring systems affect player performance on a point-to-point basis. In the cases of players like Iga Swiatek and Novak Djokovic, it's extremely difficult to point out a clear indication as to why no-ad scoring favors them, whereas with players like Elena Rybakina and John Isner, it's much clearer. Further analysis in how scoring affects service and return performance stats, such as service games won, point win rates on serve/return by first or second serve. Additionally, in aggregating player statistics, their performance is highly dependent on the opponents they face. Someone could play challengers the entire season, and perform exceptionally against lower-level competition, whereas someone like Iga Swiatek or Jannik Sinner find a lot of success in bigger tournaments. Despite facing different competition, their service and return statistics could be similar. Lastly, with more simulated matches, it is much more likely to see how the true distributions for player performance vary over the different opponents, surfaces, and scoring system they play.
