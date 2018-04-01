"""
Creates a ranking of the best players and outputs it.

Usage (from the project directory):
python3 football/main.py

Before using it, you need to have a subscription on Sportmonks.com
and put your api token into api_token.txt file.

You can adjust the variables 'league', 'date_from' and 'date_to' so
that the script analyzes the fixtures only from the leagues and dates
that you want to take into account.

It writes the ranking to the file from 'file_to_save' variable or it
prints the ranking to the standard output, if 'file_to_save' is None.
"""

from best_player_calculator import BestPlayerCalculator
from repositories import FixturesRepository, PlayersRepository
from tabulate import tabulate
from collections import OrderedDict
from os.path import dirname

max_player_count = 15000
# leagues = "2, 5, 8, 82, 163, 166, 301, 384, 564"
leagues = "82"
training_date_from = "2015-01-01"
training_date_to = "2017-01-01"
testing_date_from = "2017-01-01"
testing_date_to = "2017-06-01"
displayed_players_count = 50
file_to_save = dirname(__file__) + '/../results/bundesliga_2017.txt'
batch_size = 30

training_filter = (
    "between/" +
    training_date_from +
    "/" +
    training_date_to +
    "?leagues=" +
    leagues
)

testing_filter = (
    "between/" +
    testing_date_from +
    "/" +
    testing_date_to +
    "?leagues=" +
    leagues
)

calculator = BestPlayerCalculator(max_player_count)
fixtures_repo = FixturesRepository()
players_repo = PlayersRepository()

training_fixtures_count = fixtures_repo.get_total_count(training_filter)

batches_count = training_fixtures_count // batch_size + 1
for i in range(batches_count):
    print("Adding the training fixtures batch number " + str(i) + "...")
    fixtures = fixtures_repo.get_by_filter(
        training_filter,
        batch_size,
        batch_size * i
    )
    calculator.add_training_fixtures(fixtures)

testing_fixtures_count = fixtures_repo.get_total_count(testing_filter)

batches_count = testing_fixtures_count // batch_size + 1
for i in range(batches_count):
    print("Adding the testing fixtures batch number " + str(i) + "...")
    fixtures = fixtures_repo.get_by_filter(
        testing_filter,
        batch_size,
        batch_size * i
    )
    calculator.add_testing_fixtures(fixtures)

invalid_fixtures_count = fixtures_repo.invalid_data_count

print("All fixtures has been added.")

print("Fixtures count: " + str(training_fixtures_count))
print("Invalid fixtures count: " + str(invalid_fixtures_count))
print("Players count: " + str(calculator.players_count))
print("Testing loss: " + str(calculator.testing_loss))

best_players = calculator.get_top_players(displayed_players_count)

print("Downloading players details...")

best_players_dicts = []
for key, player in enumerate(best_players):
    player_details = players_repo.get_by_identifier(player.identifier)
    player_dict = OrderedDict([
        ('place', key + 1),
        ('full name', player_details.full_name),
        ('team', player_details.team_name),
        ('nationality', player_details.nationality),
        ('position', player_details.position),
        ('occurrences', player.occurrences),
        ('skill', player.skill)
    ])
    best_players_dicts.append(player_dict)

ranking = tabulate(best_players_dicts, 'keys')

print("All done.")

if file_to_save:
    f = open(file_to_save, 'w')
    f.write(ranking)
    f.close()
    print("The ranking has been written to the file.")
else:
    print(ranking)
