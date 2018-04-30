from context import football
import pytest as pt
import numpy as np
from football.best_player_calculator import BestPlayerCalculator
from football.entities import Player, Fixture, Substitution, Goal
from football.entities import LOCAL_TEAM, VISITOR_TEAM


def top_data_provider():
    data = []

    max_players_count = 4

    """test 1"""
    ronaldo = Player(1, "Cristiano", "Ronaldo")
    zidane = Player(2, "Zinedine", "Zidane")
    xavi = Player(3, "Xavi", "Hernandez")
    iniesta = Player(4, "Anders", "Iniesta")

    fixtures = [Fixture([ronaldo, zidane], [xavi, iniesta], 2, 0)]
    top_count = 2
    expected_players = [ronaldo, zidane]

    data.append((fixtures, top_count, max_players_count, expected_players))

    """test 2"""
    fixtures = [
        Fixture([ronaldo, zidane], [xavi, iniesta], 2, 1),
        Fixture([ronaldo, xavi], [zidane, iniesta], 1, 0),
    ]
    top_count = 1
    expected_players = [ronaldo]

    data.append((fixtures, top_count, max_players_count, expected_players))

    """test 3"""
    fixtures = [
        Fixture([xavi], [ronaldo], 1, 0),
    ]
    top_count = 1
    expected_players = [xavi]

    data.append((fixtures, top_count, max_players_count, expected_players))

    """test 4"""
    fixtures = [
        Fixture([xavi], [ronaldo], 0, 1),
    ]
    top_count = 1
    expected_players = [ronaldo]

    data.append((fixtures, top_count, max_players_count, expected_players))

    """test 5 - substitutions"""
    fixtures = [
        Fixture(
            [xavi],
            [ronaldo],
            4,
            0,
            [Substitution(zidane, xavi, 80, LOCAL_TEAM)],
            [
                Goal(LOCAL_TEAM, 20),
                Goal(LOCAL_TEAM, 42),
                Goal(LOCAL_TEAM, 82),
                Goal(LOCAL_TEAM, 84)
            ],
        ),
        Fixture(
            [xavi],
            [ronaldo],
            0,
            1,
            [Substitution(zidane, ronaldo, 70, VISITOR_TEAM)],
            [Goal(VISITOR_TEAM, 74)]
        ),
    ]
    top_count = 1
    expected_players = [zidane]

    data.append((fixtures, top_count, max_players_count, expected_players))

    """test 6 - substitutions"""
    fixtures = [
        Fixture(
            [xavi],
            [ronaldo],
            5,
            0,
            [Substitution(zidane, xavi, 80, LOCAL_TEAM)],
            [
                Goal(LOCAL_TEAM, 20),
                Goal(LOCAL_TEAM, 42),
                Goal(LOCAL_TEAM, 82),
                Goal(LOCAL_TEAM, 84),
                Goal(LOCAL_TEAM, 86)
            ],
        )
    ]
    top_count = 1
    expected_players = [zidane]

    data.append((fixtures, top_count, max_players_count, expected_players))

    """test 7 - sample_weight influenced by date"""
    fixtures = [
        Fixture(
            [xavi],
            [ronaldo],
            2,
            0,
            time=1239651697
        ),
        Fixture(
            [xavi],
            [ronaldo],
            0,
            1,
            time=1523648400
        )
    ]
    top_count = 1
    expected_players = [ronaldo]

    data.append((fixtures, top_count, max_players_count, expected_players))

    """test 8 - sample_weight influenced by date"""
    fixtures = [
        Fixture(
            [xavi],
            [ronaldo],
            2,
            0,
            time=1239651697
        ),
        Fixture(
            [xavi],
            [ronaldo],
            0,
            1,
            [Substitution(zidane, ronaldo, 45, VISITOR_TEAM)],
            [Goal(VISITOR_TEAM, 70)],
            time=1523648400
        )
    ]
    top_count = 1
    expected_players = [zidane]

    data.append((fixtures, top_count, max_players_count, expected_players))

    return data


@pt.mark.parametrize(
    "fixtures, top_count, max_players_count, expected_players",
    top_data_provider()
)
def test_get_top_players(
    fixtures,
    top_count,
    max_players_count,
    expected_players,
    monkeypatch
):
    def current_time():
        return 1523648500

    monkeypatch.setattr('time.time', current_time)
    np.random.seed(500)

    calculator = BestPlayerCalculator(max_players_count)
    calculator.add_training_fixtures(fixtures)
    returned_players = calculator.get_top_players(top_count)
    for player in expected_players:
        assert player in returned_players


@pt.mark.parametrize(
    "local_team_score, visitor_team_score, expected",
    [(2, 1, 10), (3, 0, 24), (1, 1, 0), (0, 0, 0), (0, 1, -10), (2, 3, -6)]
)
def test_convert_result_to_int(
    local_team_score,
    visitor_team_score,
    expected
):
    bpc = BestPlayerCalculator(1)
    result = bpc._convert_result_to_int(
        local_team_score,
        visitor_team_score
    )
    assert result == expected
