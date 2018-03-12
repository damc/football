import logging
from entities import Player, Fixture
import sportmonks as sm


class PlayersRepository:
    ENDPOINT = 'players'
    INCLUDE = 'team'

    @staticmethod
    def get_by_id(id):
        data = sm.get(
            PlayersRepository._get_players_endpoint(id),
            PlayersRepository.INCLUDE,
            paginated=False
        )

        player = Player(id)
        try:
            player.first_name = data['firstname']
            player.last_name = data['lastname']
            player.team_name = data['team']['data']['name']
        except Exception as e:
            logging.exception("Player data doesn't contain expected fields")

        return player

    @staticmethod
    def _get_players_endpoint(id):
        return PlayersRepository.ENDPOINT + '/' + str(id)


class FixturesRepository:
    ENDPOINT = 'fixtures'
    INCLUDE = 'lineup'
    PER_PAGE = 100

    def __init__(self):
        self.fixtures = {}

    def get_by_filter(self, filter, limit, offset):
        if filter not in self.fixtures:
            data = sm.get(
                FixturesRepository._get_fixtures_endpoint(filter),
                FixturesRepository.INCLUDE,
                paginated=False
            ) or 0

            fixtures = []
            for data_sample in data:
                fixtures.append(self._convert_to_fixture(data_sample))

            self.fixtures[filter] = fixtures

        return self.fixtures[filter][offset:(offset + limit)]

    @staticmethod
    def get_total_count(filter):
        return sm.get_total_count(
            FixturesRepository._get_fixtures_endpoint(filter)
        )

    @staticmethod
    def _convert_to_fixture(data_sample):
        try:
            local_team_id = data_sample['localteam_id']
            visitor_team_id = data_sample['visitorteam_id']

            local_team_score = data_sample['scores']['localteam_score']
            visitor_team_score = data_sample['scores']['visitorteam_score']

            local_team_players = []
            visitor_team_players = []

            lineup_data = data_sample['lineup']['data']
            for player_data in lineup_data:
                # to do: omit fixture instead assigning 0
                player = Player(player_data['player_id'] or 0)

                if player_data['team_id'] == local_team_id:
                    local_team_players.append(player)
                elif player_data['team_id'] == visitor_team_id:
                    visitor_team_players.append(player)
                else:
                    raise ValueError("Player doesn't belong to any team")
        except Exception as e:
            logging.exception("Fixtures data is invalid")

        return Fixture(
            local_team_players,
            visitor_team_players,
            local_team_score,
            visitor_team_score
        )

    @staticmethod
    def _get_fixtures_endpoint(filter=""):
        return FixturesRepository.ENDPOINT + '/' + filter
