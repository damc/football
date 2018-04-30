"""Creates a ranking of the best players."""

import numpy as np
from keras.constraints import non_neg
from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import SGD
from time import time
from entities import LOCAL_TEAM, VISITOR_TEAM


class BestPlayerCalculator:
    """Creates a ranking of the best players."""

    STANDARD_MATCH_LENGTH = 90
    EPOCHS_COUNT = 32
    LEARNING_RATE = 0.01

    CONVERT_RESULT_POWER = 0.8
    CONVERT_RESULT_MULTIPLY = 10

    SAMPLE_WEIGHT_DATE_MULTIPLY = 0.000000005

    def __init__(self, max_players_count, time_=None):
        """
        Class constructor.

        :param max_players_count: int
        :param time_: int
        """
        self.time = time_ or time()
        self._players = {}
        self.players_count = 0
        self._first_layer_size = max_players_count + 1
        self._testing_loss = 0
        self._testing_batches_count = 0

        self._model = Sequential()
        self._model.add(
            Dense(
                1,
                input_dim=self._first_layer_size,
                kernel_constraint=non_neg(),
                use_bias=False,
                activation='linear'
            )
        )

        sgd = SGD(self.LEARNING_RATE)
        self._model.compile(loss='mean_squared_error', optimizer=sgd)

    def add_training_fixtures(self, fixtures):
        """
        Add fixtures used as a training data.

        :param fixtures: list of Fixture
        :return:
        """
        prepared = []
        for fixture in fixtures:
            self._update_players(fixture.get_all_players())
            prepared += self._prepare_samples(fixture)

        n = len(prepared)

        x = np.empty((n, self._first_layer_size))
        y = np.empty((n,))
        weights = np.empty((n,))

        for key, data in enumerate(prepared):
            x[key] = data['x']
            y[key] = data['y']
            weights[key] = data['weight']

        # @todo use fit_generator()
        self._model.fit(
            x,
            y,
            epochs=self.EPOCHS_COUNT,
            sample_weight=weights,
            verbose=0
        )

    def add_testing_fixtures(self, fixtures):
        """
        Add testing fixtures for estimating testing loss.

        :param fixtures: list of Fixture
        :return: boolean
        """
        prepared = []
        for fixture in fixtures:
            if not self._can_fixture_be_evaluated(fixture):
                continue
            prepared += self._prepare_samples(fixture)

        n = len(prepared)
        if n == 0:
            return False

        # @todo Don't repeat yourself
        x = np.empty((n, self._first_layer_size))
        y = np.empty((n,))
        weights = np.empty((n,))

        for key, data in enumerate(prepared):
            x[key] = data['x']
            y[key] = data['y']
            weights[key] = data['weight']

        self._testing_loss += self._model.evaluate(
            x,
            y,
            sample_weight=weights,
            verbose=0
        )
        self._testing_batches_count += 1
        return True

    def get_top_players(self, count):
        """
        Return best players according to the calculator.

        :param count: int
        :return: list of Player
        """
        players_list = list(self._players.values())

        weights = self._model.get_weights()[0]
        for key, player in enumerate(players_list):
            players_list[key].skill = weights.item((player.node_id,))

        players_list.sort(key=lambda p: p.skill, reverse=True)

        return players_list[:count]

    def get_testing_loss(self):
        """
        Return loss for testing data.

        :return: int
        """
        if self._testing_batches_count:
            return self._testing_loss / self._testing_batches_count
        return 0

    def _prepare_samples(self, fixture):
        substitutions_count = len(fixture.substitutions)
        samples = []
        for i in range(0, substitutions_count + 1):
            sample_minute_from = (
                0 if i == 0 else fixture.substitutions[i - 1].minute
            )
            sample_minute_to = (
                fixture.match_length if i == substitutions_count
                else fixture.substitutions[i].minute
            )

            x = self._calculate_x(
                fixture,
                sample_minute_from,
                sample_minute_to
            )
            y = self._calculate_y(
                fixture,
                sample_minute_from,
                sample_minute_to
            )
            weight = self._calculate_weight(
                fixture,
                sample_minute_from,
                sample_minute_to
            )

            if weight == 0:
                continue

            samples.append({'x': x, 'y': y, 'weight': weight})

        return samples

    def _calculate_x(self, fixture, sample_minute_from, sample_minute_to):
        x = np.zeros((self._first_layer_size,))
        all_players = fixture.get_all_players()
        for player in all_players:
            node_id = self._players[player.identifier].node_id
            x[node_id] = self._calculate_x_for_player(
                fixture,
                player,
                sample_minute_from,
                sample_minute_to
            )
        return x

    @staticmethod
    def _calculate_x_for_player(
            fixture,
            player,
            sample_minute_from,
            sample_minute_to
    ):
        if player in fixture.get_local_team_players_and_substitutes():
            team = LOCAL_TEAM
        elif player in fixture.get_visitor_team_players_and_substitutes():
            team = VISITOR_TEAM
        else:
            raise ValueError("Player doesn't belong to any team")

        minutes_played = fixture.get_minutes_played(
            player,
            sample_minute_from,
            sample_minute_to
        )

        if minutes_played > 0 and team == LOCAL_TEAM:
            return 1
        if minutes_played > 0 and team == VISITOR_TEAM:
            return -1
        return 0

    def _calculate_y(self, fixture, sample_minute_from, sample_minute_to):
        # @todo clean up mess
        result_before = fixture.get_result_in_minute(sample_minute_from)
        local_team_score, visitor_team_score = result_before
        result_before_int = self._convert_result_to_int(
            local_team_score,
            visitor_team_score
        )

        result_after = fixture.get_result_in_minute(sample_minute_to)
        local_team_score, visitor_team_score = result_after
        result_after_int = self._convert_result_to_int(
            local_team_score,
            visitor_team_score
        )

        sample_length = sample_minute_to - sample_minute_from
        ratio = (
            self.STANDARD_MATCH_LENGTH / sample_length if sample_length > 0
            else 0
        )

        return (result_after_int - result_before_int) * ratio

    def _calculate_weight(
        self,
        fixture,
        sample_minute_from,
        sample_minute_to
    ):
        sample_length = sample_minute_to - sample_minute_from
        weight_by_minutes = sample_length / self.STANDARD_MATCH_LENGTH

        weight_by_date = 1
        if fixture.time is not None:
            time_length = abs(self.time - fixture.time)
            weight_by_date = max(
                1 - time_length * self.SAMPLE_WEIGHT_DATE_MULTIPLY,
                0
            )

        return weight_by_minutes * weight_by_date

    def _convert_result_to_int(self, local_team_score, visitor_team_score):
        if local_team_score > visitor_team_score:
            ratio = (
                local_team_score / visitor_team_score - 1
                if visitor_team_score > 0
                else local_team_score
            )
        else:
            ratio = (
                visitor_team_score / local_team_score - 1
                if local_team_score > 0
                else visitor_team_score
            )

        multiplied = round((
            ratio **
            self.CONVERT_RESULT_POWER *
            self.CONVERT_RESULT_MULTIPLY
        ))

        return (
            multiplied
            if local_team_score > visitor_team_score
            else -multiplied
        )

    def _can_fixture_be_evaluated(self, fixture):
        for player in fixture.get_all_players():
            if player.identifier not in self._players:
                return False
        return True

    def _update_players(self, players_in_fixture):
        for player in players_in_fixture:
            self._add_player(player)
            self._increment_player_occurrences(player)

    def _add_player(self, player):
        if player.identifier not in self._players:
            self._players[player.identifier] = player
            self._players[player.identifier].node_id = self.players_count
            self.players_count += 1

    def _increment_player_occurrences(self, player):
        if hasattr(self._players[player.identifier], 'occurrences'):
            self._players[player.identifier].occurrences += 1
        else:
            self._players[player.identifier].occurrences = 1
