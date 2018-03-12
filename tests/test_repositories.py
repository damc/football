from context import football
import json
from os.path import dirname
from football.repositories import FixturesRepository
from football.entities import Player, Fixture


def test_get_by_filter_returns_correct_fixtures(monkeypatch):
    def mock_get(fixtures, include):
        fixtures_file = dirname(__file__) + '/test_json/fixtures.json'
        return json.loads(open(fixtures_file).read(100000))

    monkeypatch.setattr('football.sportmonks.get', mock_get)

    expected_fixtures = [
        Fixture([Player(6979), Player(12100)], [], 0, 2),
        Fixture([Player(4357)], [Player(6013397)], 3, 2)
    ]

    fixtures_repo = FixturesRepository()
    for i in range(0, 2):  # assert two times to test caching
        fixtures = fixtures_repo.get_by_filter('random_filter', 2, 2)
        assert fixtures == expected_fixtures
