# Football

This program creates a ranking of the best football players basing on the analysis of the matches/fixtures downloaded from Sportmonks API.

What is understood by "a good player"? Football is a team sport. Therefore how good the player is is defined as how much he increases the probability of a win of the team in which he plays by playing in this team.

In other words, this program uses mathematical approach to find out which players increase the probability of his team winning the most.

## Usage

Before you run the program, you have to have a subscription on Sportmonks.com and API token so that the program can connect to Sportmonks API. You have to have Python3 installed as well.

To install, run ``install.sh``. It will ask you for API token to Sportkmonks API and install the required packages.

To run the program, execute (from the project root folder):

```
python3 football/main.py
```

## How does the algorithm work

### tl;dr

It uses a linear regression for accomplishing the task.

The algorithm is trained to predict the results of matches (y) taking the players playing in the match as an input (_x_)

Let's suppose that:

1. y - a real number representing how much the local team won over the visitor team in the given match. So y > 0 if the local team is the winner, y = 0 in case of draw, y < 0 if the visitor team is the winner.

2. _x_[i] = 1, if the player with id = i played in the local team, _x_[i] = -1, if the player with i = i played in the visitor team, _x_[i] = 0 if the player with i = 0 didn't play in the match.

If we have a model like this:

y = &sum;i (_x_[i] * _w_[i])

and we train _w_ to give predictions of y (the result of the match converted to a single integer) basing on _x_ (who played in the match and in which team), then _w_[i] will become higher if the player with id = i is good and lower if the player with id = i is weak (basing on the given input).

In the below explanation, the weights are denoted with _s_ (from "skill") instead of _w_.

### Data set

Each data sample of the input data set is a description of one fixture (match) and consists of the following information:

1. Players playing from the first minute in the local team.
2. Players playing from the first minute in the visitor team.
3. Result of the match.
4. Match length (it's sometimes longer than 90 minutes due to extra time).
5. Substitutions made (who came in, who came out, in which minute).
6. Goals (which team scored, in which minute).

### Model

In order to make the explanation simpler, let's suppose that we have only the first three information of the data sample for now (without match length, substitutions and goals).

Assuming that each player has it's unique integer ID, we can represent the players playing in the match as a vector _x_ in which:

_x_[i] = 1, if the player with id = i plays in a local team,

_x_[i] = -1, if the player with id = i plays in a visitor team,

_x_[i] = 0, if the player with id = i doesn't play in the match at all

The length of the vector is the amount of all players (assuming that the IDs are given in order).

For example:

The local team players ids are: 2, 3, 4;

The visitor team players ids are: 7, 8, 9;

There are also players with ids 1, 5, 6, 10, 11, 12, 13, 14 and 15 that doesn't play in the match;

In this case _x_ = [0, 1, 1, 1, 0, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0] (indexed from 1)

The result of the match can be converted to one real number y which represents how strongly the local team won over visitor team. If the local team won the match, then y > 0. If the match ended with a draw, then y = 0. If the visitor team won, then y < 0. y can be the difference of the local team score and visitor team score for example, but it's a little bit different than that in the program.

Let's suppose that on average:

y = f(l - v)

Where:

l - local team strength,
v - visitor team strength,
f(x) - some function so that for every real number x: f(x)' > 0 (it has higher value for higher x and lower value for lower x) and f(x) = 0.

For simplicity of explanation, let's just assume that:

y = l - v

Let's also assume that the strength of the team is the sum of the skills of all the players in the team individually. This assumption is wrong because Xavi and Iniesta can be stronger in one team than Xavi and Ronaldo in one team, even if Ronaldo is individually better than Iniesta. But for estimating the skills of the players (which is what this algorithm does) this assumption is ok.

We can represent this assumption as follows:

l = &sum;i (_l_[i] * _s_[i]) (from i = 1 to i = amount of all players):

v = &sum;i (_v_[i] * _s_[i]) (from i = 1 to i = amount of all players):

Where:

l - local team strength

v - visitor team strength

_l_[i] = 1 if the player with ID = i is in the local team, else it equals 0.

_v_[i] = 1 if the player with ID = i is in the visitor team, else it equals 0.

_s_[i] = skill of the player with ID = i (how good this player is).

As we said before:

y = l - v

Therefore:

y = &sum;i (_l_[i] * _s_[i]) - &sum;i (_v_[i] * _s_[i]) (from i = 1 to i = amount of all players)

Therefore:

y = &sum;i (_x_[i] * _s_[i]) (from i = 1 to i = amount of all players)

where:

y - a real number representing how much the local team won over the visitor team, y > 0 if the local team is the winner, y = 0 in case of draw, y < 0 if the visitor team is the winner
 
_x_[i] = 1, if the player with id = i plays in the local team, _x_[i] = -1, if the player with i = i plays in the visitor team, _x_[i] = 0 if the player with i = 0 doesn't play in the match

_s_[i] = skill of the player with ID = i (how good this player is)

The last equation is our model. The model is trained to predict the results of the matches (y) taking as an input the players in the match (_x_).
 
 The goal is to find _s_ such that the value of cost function which represents how much our estimated y differs from the real y on all data samples is the lowest. I used Keras library and SGD algorithm to achieve this goal.
 
 At the end of the training _s_[i] will contain the skill of the player with ID = i basing on the matches that we provided as an input.
 
### Substitutions and goals

We have also the following data about every match:
...
4. Match length (it's sometimes longer than 90 minutes due to extra time).
5. Substitutions made (who came in, who came out, in which minute).
6. Goals (which team scored, in which minute).

To make use of this information, every match is divided into smaller matches (smaller data samples) with the minutes when substitutions were made as a delimiter. 'y' variable is set to the result of the match only taking into account that period of time which the data sample represent. The sample weight of the data sample equals how long was the period divided by match length.

The above explanation is probably not clear, so I'll give an example:

Let's suppose that the data is like this:
1. Local team players: 2, 3, 4.
2. Visitor team playes: 7, 8, 9.
3. The result of the match: 2:1 (local team won).
4. Substitutions:
a) the player 4 was replaced with the player 5 in the.
b) the player 7 was replaced with the player 6.