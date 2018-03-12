from context import football
import pytest as pt
from football.entities import Player, Fixture, Substitution, Goal
from football.entities import LOCAL_TEAM, VISITOR_TEAM


def test_fixture_has_correct_substitutes():
    ronaldo = Player(1, "Cristiano", "Ronaldo")
    zidane = Player(2, "Zinedine", "Zidane")
    xavi = Player(3, "Xavi", "Hernandez")
    iniesta = Player(4, "Anders", "Iniesta")

    fixture = Fixture(
        [ronaldo],
        [xavi],
        0,
        0,
        [
            Substitution(zidane, ronaldo, 50, LOCAL_TEAM),
            Substitution(iniesta, xavi, 60, VISITOR_TEAM)
        ]
    )

    assert fixture.local_team_substitutes == [zidane]
    assert fixture.visitor_team_substitutes == [iniesta]


def get_minutes_provider():
    ronaldo = Player(1, "Cristiano", "Ronaldo")
    zidane = Player(2, "Zinedine", "Zidane")
    xavi = Player(3, "Xavi", "Hernandez")

    fixture = Fixture(
        [ronaldo],
        [xavi],
        0,
        0,
        [Substitution(zidane, ronaldo, 50, LOCAL_TEAM)]
    )

    return [
        (fixture, zidane, 0, None, 40),
        (fixture, ronaldo, 0, None, 50),
        (fixture, xavi, 0, None, 90),
        (fixture, xavi, 30, 70, 40),
        (fixture, xavi, 45, None, 45),
        (fixture, xavi, 0, 70, 70),
        (fixture, zidane, 40, 60, 10),
        (fixture, zidane, 60, 80, 20),
        (fixture, zidane, 30, None, 40),
        (fixture, zidane, 0, 80, 30),
        (fixture, ronaldo, 30, 55, 20),
        (fixture, ronaldo, 30, None, 20),
        (fixture, ronaldo, 0, 80, 50)
    ]

@pt.mark.parametrize(
    "fixture, player, minute_from, minute_to, expected",
    get_minutes_provider()
)
def test_get_minutes_played(
        fixture,
        player,
        minute_from,
        minute_to,
        expected
):
    result = fixture.get_minutes_played(player, minute_from, minute_to)
    assert result == expected


def test_get_result_in_minute():
    ronaldo = Player(1, "Cristiano", "Ronaldo")
    zidane = Player(2, "Zinedine", "Zidane")

    fixture = Fixture(
        [ronaldo],
        [zidane],
        1,
        2,
        goals=[
            Goal(LOCAL_TEAM, 10),
            Goal(VISITOR_TEAM, 40),
            Goal(VISITOR_TEAM, 75)
        ]
    )

    assert fixture.get_result_in_minute(5) == {
        "local_team_score": 0,
        "visitor_team_score": 0
    }
    assert fixture.get_result_in_minute(15) == {
        "local_team_score": 1,
        "visitor_team_score": 0
    }
    assert fixture.get_result_in_minute(50) == {
        "local_team_score": 1,
        "visitor_team_score": 1
    }
    assert fixture.get_result_in_minute(80) == {
        "local_team_score": 1,
        "visitor_team_score": 2
    }