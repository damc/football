from best_player_calculator import BestPlayerCalculator
from repositories import FixturesRepository, PlayersRepository
from tabulate import tabulate

max_player_count = 15000
leagues = "2,5,8,82,163,166,301,384,564"
fixtures_filter = "between/2015-03-18/2018-03-18?leagues=" + leagues

batch_size = 30
displayed_players_count = 50

calculator = BestPlayerCalculator(max_player_count)
fixtures_repo = FixturesRepository()
players_repo = PlayersRepository()

fixtures_count = fixtures_repo.get_total_count(fixtures_filter)
print("Fixtures count: " + str(fixtures_count))

batches_count = fixtures_count // batch_size + 1
for i in range(batches_count):
    print("Adding the fixtures batch number " + str(i) + "...")
    fixtures = fixtures_repo.get_by_filter(
        fixtures_filter,
        batch_size,
        batch_size * i
    )
    calculator.add_fixtures(fixtures)

print("All fixtures has been added.")

best_players = calculator.get_top_players(displayed_players_count)

print("Downloading players details...")

best_players_dicts = []
for key, player in enumerate(best_players):
    player_dict = vars(players_repo.get_by_id(player.id))
    player_dict['skill'] = player.skill
    player_dict['occurrences'] = player.occurrences
    player_dict['place'] = key + 1
    best_players_dicts.append(player_dict)

print("All done.")

print(tabulate(best_players_dicts, 'keys'))
