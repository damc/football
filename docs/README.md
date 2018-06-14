Hello guys.

You’ve maybe heard about The Best Football Player Award. The ranking where Cristiano Ronaldo or Messi always wins and Neymar is at the third place. At the end of the last year, when I heard about this award, I was thinking about the imperfectness of the method how the best player is chosen. The best player is chosen with the votes of journalists and coaches which means for example that if there are more journalists from Spain, the players from Spanish league are more likely to win (to be fair, I’m not sure how it works, but I’m sure it’s not perfect). I was thinking about better way and I’ve created a computer program that uses machine learning to learn how good players are and who is the best football player in the world. My way is not necesarilly better, but it's based on different information therefore it can tell something that we don't know.

Before I show the results and describe the algorithm, I want to ask you about one thing. There are many possible misunderstandings that can arise about this algorithm when you read about this. Because of that, if you want to say that this algorithm sucks, please do the following:
1. Go to the bottom of that page, to the section "Frequently asked questions and misunderstandings".
2. See if you can find an answer to your reason why you think that this algorithm sucks. If you can, read it.
3. If you can't find your reason or you are not satisfied with the answer, then now you can say that this algorithm sucks.

How does it define who is good and who is not? Football is a team sport, therefore we assume that the best player is that player which increases the probability of a team winning the most.

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

Looks like you can't tell a lot about how good players are basing on that information, doesn't it? That's partly true, but if you analyze a lot of matches and make good use of these information, then you can tell more than it seems.
Notice that the algorithm does NOT have information about who scored the goals (it has only information about which team scored and in which minute, but not which player scored the goal), which player is popular or which player is most handsome. Therefore, the algorithm is completely objective. It takes into account only who was at the pitch in which minute and in which minute the goal was scored for which team.

# How does the algorithm work

In short, the algorithm is trained to predict the result of matches, but the model is constructed in such way that the weights used in the model to make predictions at the end of training will represent how good the player is.

If you analyze the algorithm, you can notice that in practice the players at the top of the ranking will be mostly the players which meet the below criteria the most:
1. They play in the good teams (those teams that win a lot, taking into account with whom they play).
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
