

This program creates a ranking of the best football players basing only on the below data.

# Data

The algorithm has analysed all of the matches from the last 5 years to learn who is the best (I took the data from sportmonks.com API).

These are the data that were given to the algorithm about each match:

* Players playing from the first minute in the local team. 
* Players playing from the first minute in the visitor team. 
* Result of the match. 
* Match length (it's sometimes longer than 90 minutes due to extra time). 
* Substitutions made (who came in, who came out, in which minute). 
* Goals (which team scored, in which minute). 
* The date of the match.
* Positions on which every player played <-- not done yet.

It looks like you can't tell a lot about how good players are basing on that information, doesn't it? This is partly true, but if you analyze a lot of matches and make good use of these information, then you can tell more than it seems.
Notice that the algorithm does NOT have information about who scored the goals (it has only information about which team scored and in which minute, but not which player scored the goal). It takes into account only who was at the pitch in which minute and in which minute the goal was scored for which team.

The point of this project is that human usually rates the skill of a player by how many goals he scores, how good tricks he makes etc. But this program actually measures how the presence of a player in a team affects the result, from statistical point of view based on previous matches. So for example, let's suppose that there is a player who scores a lot of goals and we all think that he is good. But let's suppose that he always gets good passes from a midfilder and that's why he scores a lot of goals. If we replace him with another striker, the results of the matches will be similar, because the cause of good results of the team in this case is not the striker, but the midfilder. To a human eye, the striker is very good. But in the ranking created by the program, in this case, the midfider will have a high result and the striker will have an average result, because the midfilder is who makes the good result, not the striker. Another example is: let's suppose that there is a defender who regurarly does good job and thanks to him the team achieves good results. For a human eye, he can remain unnoticed. But the program analyzing the results of the matches will rate him high, because when he is on the pitch, the team achieves better results than when he is not.

# How does the algorithm work

In short, the algorithm is trained to predict the result of matches, but the model is constructed in such way that the weights used in the model to make predictions at the end of training will represent how good the player is.

If you analyze the algorithm, you can notice that in practice the players at the top of the ranking will be mostly the players which meet the below criteria the most:
1. They play in good teams (those teams that win a lot, taking into account with whom they play).
2. When they play in their team, their team achieves better results than when they are not present on the pitch.
3. If national teams are included, they increase the level of their national team (meaning that their team play surprisingly well with them taking into account the level of other players in the team).

You can find more detailed explanation of how it works in the readme file.

# Results

The algorithm analysed 23788 matches and took into account 25196 players – all matches and players from the following leagues and competitions during last 5 years:

World Cup Qualification Worldwide (all of the continents) + World Cup, Copa America, European Championship, Champions league (including qualifications), Europa league, English league, German league, French league, Italian league, Spanish league, Brazilian league, Argentinian league, Dutch league, Portuguese leauge, Scottish league, Turkish league, Fifa Club World Cup, Copa Libertadores, CONCACAF Champions League, CONCACAF Gold Cup, Confederations Cup, Africa Cup of Nations.

The below ranking shows top 10 best players in the world at the current moment according to the machine learning algorithm:

| place | full name                           | current team    | nationality           | position    | occurences  | skill   |
| :---: | :---------------------------------: | :-------------: | :-------------------: | :---------: | :---------: | :-----: |
| 1     | David Alaba                         | Bayern München  | Austria               | Defender    | 170         | 6.76027 |
| 2     | Cristiano Ronaldo                   | Real Madrid     | Portugal              | Attacker    | 218         | 6.2646  |
| 3     | Mohamed  Salah                      | Liverpool       | Egypt                 | Attacker    | 174         | 5.63545 |
