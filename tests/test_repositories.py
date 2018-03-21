from context import football
import json
from os.path import dirname
from football.repositories import FixturesRepository
from football.entities import Player, Fixture, Substitution, Goal
from football.entities import LOCAL_TEAM, VISITOR_TEAM


def test_get_by_filter(monkeypatch):
    def mock_get(fixtures, include, paginated=None):
        fixtures_file = dirname(__file__) + '/test_json/fixtures.json'
        return json.loads(open(fixtures_file).read(100000))

    monkeypatch.setattr('football.sportmonks.get', mock_get)

    expected_fixtures = [
        Fixture(
            [Player(6979), Player(12100)],
            [],
            0,
            2,
            [
                Substitution(Player(2460), Player(6979), 53, LOCAL_TEAM),
                Substitution(Player(2461), Player(12100), 75, LOCAL_TEAM)
            ],
            [Goal(LOCAL_TEAM, 30)]
        ),
        Fixture([Player(4357)], [Player(6013397)], 3, 2, [], [])
    ]

    fixtures_repo = FixturesRepository()
    for i in range(0, 2):  # assert two times to test if caching doesn't break
        fixtures = fixtures_repo.get_by_filter('random_filter', 2, 2)
        assert fixtures == expected_fixtures
