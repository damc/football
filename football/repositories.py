import logging
from entities import Player, Fixture, Substitution, Goal
from entities import LOCAL_TEAM, VISITOR_TEAM
import sportmonks as sm


class PlayersRepository:
    ENDPOINT = 'players'
    INCLUDE = 'team,position'

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
            player.position = data['position']['data']['name']
        except KeyError:
            logging.exception("Player data doesn't contain expected fields")

        return player

    @staticmethod
    def _get_players_endpoint(id):
        return PlayersRepository.ENDPOINT + '/' + str(id)


class FixturesRepository:
    ENDPOINT = 'fixtures'
    INCLUDE = 'lineup,substitutions,goals'
    PER_PAGE = 100

    def __init__(self):
        self.fixtures = {}

    def get_by_filter(self, filter, limit, offset):
        if filter not in self.fixtures:
            data = sm.get(
                FixturesRepository._get_fixtures_endpoint(filter),
                FixturesRepository.INCLUDE,
                paginated=False
            ) or []

            fixtures = []
            for data_sample in data:
                fixture = self._convert_to_fixture(data_sample)
                if fixture:
                    fixtures.append(fixture)

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
                if player_data['player_id'] is None:
                    raise ValueError("Player id is null")

                player = Player(player_data['player_id'])

                player_data['team_id'] = int(player_data['team_id'])
                if player_data['team_id'] == local_team_id:
                    local_team_players.append(player)
                elif player_data['team_id'] == visitor_team_id:
                    visitor_team_players.append(player)
                else:
                    raise ValueError("Player doesn't belong to any team")

            substitutions = []
            substitutions_data = data_sample['substitutions']['data']
            for substitution_data in substitutions_data:
                player_in = Player(substitution_data['player_in_id'])
                player_out = Player(substitution_data['player_out_id'])
                minute = substitution_data['minute']

                # @todo fix this correctly
                if not minute:
                    raise ValueError("Goal doesn't have minute")

                team = (
                    LOCAL_TEAM
                    if int(substitution_data['team_id']) == local_team_id
                    else VISITOR_TEAM
                )
                substitution = Substitution(
                    player_in,
                    player_out,
                    minute,
                    team
                )
                substitutions.append(substitution)

            goals = []
            goals_data = data_sample['goals']['data']
            for goal_data in goals_data:
                team = (
                    LOCAL_TEAM
                    if int(goal_data['team_id']) == local_team_id
                    else VISITOR_TEAM
                )
                minute = goal_data['minute']

                # @todo fix this correctly
                if not minute:
                    raise ValueError("Goal doesn't have minute")

                goal = Goal(team, minute)
                goals.append(goal)

            match_length = data_sample['time']['minute']

            return Fixture(
                local_team_players,
                visitor_team_players,
                local_team_score,
                visitor_team_score,
                substitutions,
                goals,
                match_length
            )
        except (KeyError, ValueError):
            logging.exception("Fixtures data are invalid")
            return None

    @staticmethod
    def _get_fixtures_endpoint(filter=""):
        return FixturesRepository.ENDPOINT + '/' + filter
