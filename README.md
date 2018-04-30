# Football

This program creates a ranking of the best football players basing on the analysis of the matches/fixtures downloaded from Sportmonks API.

What is understood by "a good player"? Football is a team sport. Therefore how good the player is is defined as how much he increases the probability of a win of the team in which he plays.

In other words, this program uses mathematical approach to find out which players increase the probability of his team winning the most.

## Installation

1. Install required packages from requirements.txt file using pip3.
2. Create an account on Sportmonks.com and put your api token into api_token.txt file.

## Usage

Before you run the program, you have to have a subscription on Sportmonks.com and API token so that the program can connect to Sportmonks API. You have to have Python3 installed as well.

To run the program, execute (from the project root folder):

```
python3 football/main.py
```

## How does the algorithm work

### General idea

It uses a linear regression model for accomplishing the task.

If you're not familiar with linear regression, you need to read about it first. Here  you have a simple explanation (choose one of these links that better fits you):

https://medium.com/simple-ai/linear-regression-intro-to-machine-learning-6-6e320dbdaf06
https://www.spss-tutorials.com/multiple-linear-regression/

The algorithm is trained to predict the results of matches (y) taking the players playing in the match as an input (_x_)

Let's suppose that:

1. y - a real number representing how much the local team won over the visitor team in the given match. So y > 0 if the local team is the winner, y = 0 in case of draw, y < 0 if the visitor team is the winner.

2. _x_[i] = 1, if the player with id = i (all players have some id assigned) played in the local team, _x_[i] = -1, if the player with id = i played in the visitor team, _x_[i] = 0 if the player with id = i didn't play in the match.

If we have a model like this:

y = _x_[1] * _w_[1] + _x_[2] * _w_[2] + ... + _x_[n] * _w_[n]

and we train _w_ (weights) to give correct predictions of y (the result of the match converted to a single real number) basing on _x_ (who played in the match and in which team), then after training _w_[i] will be as high as good the player with id = i is (basing on the given input).

Why?

We want to learn how the presence of a player in the team affects the result of the match. So if the player with id = i plays in the first team, then _x_[i] = 1 because he has positive impact on the result (y) - the better he is, the more positive impact he will have on the value of this variable. If he doesn't play, then he doesn't have any impact on the result (y) so x[i] = 0. If he plays in the second team, then he has negative impact on the result (y) so x[i] = -1 - the better he is, the more negative impact he will have on the value of this variable. This way, w[i] will be high if he's good and it will be low if he's weak.

The above model wouldn't be perfect if we wanted to get predictions of the results of the matches because linear regression can't represent for example that two players are good together (for example Xavi and Iniesta can play well and be strong together). The model assumes that the result of the match is a consequence of the strength of all players individually. So if we wanted to get the predictions of matches, the neural network model would be better because it can represent that two players are good together (and we could add more variables as an input than just players). But if we want to learn what is the influence of individual players to the result, then this model is great.

### Data set

The algorithm analyzes football matches. The algorithm is given the following information about each match:

1. Players playing from the first minute in the local team.
2. Players playing from the first minute in the visitor team.
3. Result of the match.
4. Match length (it's sometimes longer than 90 minutes due to extra time).
5. Substitutions made (who came in, who came out, in which minute).
6. Goals (which team scored, in which minute).
7. The date of the match.
 
### Substitutions and goals

In "General idea" section, I explained how the algorithm uses the first three information (players playing in the first team, the second team and the result of the match). But we have also the following data about every match:

...

4. Match length (it's sometimes longer than 90 minutes due to extra time).

5. Substitutions made (who came in, who came out, in which minute).

6. Goals (which team scored, in which minute).

To make use of this information, every match is divided into smaller matches (smaller data samples) with the minutes when substitutions were made as a delimiter.

_x_[i] in each sample represents if player with ID = i played at the time represented by given sample.

y variable is set to the result of the match only taking into account that period of time which the data sample represent. 'y' is multiplied by (match_length / sample_time) because it represents how much the local team beaten the visitor team and if they scored more goals in the short time then they beaten them more than if they scored it in a long time. The sample weight of the data sample representing this period equals how long was the period divided by match length.

The above explanation is probably not clear, so I'll give an example:

Let's suppose that the data is like this:

1. Local team players: 2, 3, 4.

2. Visitor team playes: 7, 8, 9.

3. The result of the match: 2:1 (local team won).

4. Substitutions:

a) The player 4 was replaced with the player 5 in the 30 minute.

b) The player 7 was replaced with the player 6 in the 60 minute.

5. Goals:

a) The first goal was scored in 20 minute by the visitor team.

b) The second goal was scored in 70 minute by the local team.

c) The third goal was scored in 80 minute by the local team.

We divide this match into three data sample:

1. One represents the period of time from 0 minute to 30 minute (time of the first substitution).

2. The second one represents the period of time from 30 minute to 60 minute (time of the second substitution).

3. The third one represents the period of time from 60 minute to 90 minute.

The first data sample will be like this:

_x_ = [0, 1, 1, 1, 0, 0, -1, -1, -1, 0] (indexed from 1) (because those players played from 0 to 30 minute)

_y_ = (-1) * (90 / 30) = -3 (the result was -1, but it was in only 30 minutes, so we multiply it by 3)

sample_weight = 30 / 90 = 1/3 (it is only 1/3 of the match so importance of this sample is 1/3)

The second data sample will be like this:

_x_ = [0, 1, 1, 0, 1, 0, -1, -1, -1, 0] (indexed from 1) (the player 4 was substituted by player 5 in the local team)

_y_ = 0 * (90 / 30) = 0 (the result is 0 because there were no goals in this part of match)

sample_weight = 30 / 90 = 1/3 (it is only 1/3 of the match so importance of this sample is 1/3)

The third data sample will be like this:

_x_ = [0, 1, 1, 0, 1, -1, 0, -1, -1, 0] (indexed from 1) (the player 7 was substituted by player 6 in the visitor team)

_y_ = -2 * (90 / 30) = -6 (visitor team won 2:0 in this part, so the result is -2 multiplied by 3 because it's only 1/3 of the match)

sample_weight = 30 / 90 = 1/3 (it is only 1/3 of the match so importance of this sample is 1/3)

### Date of the match

The date of the match only affects the sample weight because if we want to know who is the best player at this moment, then the match that was yesterday is more important than the match that was 10 years ago. Cristiano Ronaldo wasn't 10 years ago as good as he is now, so if we want to know how good he is now, then we should take the match from yesterday into account more than the match from 10 years ago.
