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
    iniesta = Player(4, "Anders", "Iniesta")

    fixture1 = Fixture(
        [ronaldo],
        [xavi],
        0,
        0,
        [Substitution(zidane, ronaldo, 50, LOCAL_TEAM)]
    )

    fixture2 = Fixture(
        [xavi],
        [ronaldo],
        0,
        0,
        [
            Substitution(zidane, ronaldo, 50, VISITOR_TEAM),
            Substitution(iniesta, zidane, 60, VISITOR_TEAM)
        ]
    )

    return [
        (fixture1, zidane, 0, None, 40),
        (fixture1, ronaldo, 0, None, 50),
        (fixture1, xavi, 0, None, 90),
        (fixture1, xavi, 30, 70, 40),
        (fixture1, xavi, 45, None, 45),
        (fixture1, xavi, 0, 70, 70),
        (fixture1, zidane, 40, 60, 10),
        (fixture1, zidane, 60, 80, 20),
        (fixture1, zidane, 30, None, 40),
        (fixture1, zidane, 0, 80, 30),
        (fixture1, ronaldo, 30, 55, 20),
        (fixture1, ronaldo, 30, None, 20),
        (fixture1, ronaldo, 0, 80, 50),
        (fixture2, ronaldo, 0, None, 50),
        (fixture2, zidane, 0, None, 10),
        (fixture2, zidane, 35, 55, 5),
        (fixture2, iniesta, 40, None, 30),
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

    assert fixture.get_result_in_minute(5) == (0, 0)
    assert fixture.get_result_in_minute(15) == (1, 0)
    assert fixture.get_result_in_minute(50) == (1, 1)
    assert fixture.get_result_in_minute(80) == (1, 2)
