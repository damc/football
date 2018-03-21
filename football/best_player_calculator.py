import numpy as np
from keras.constraints import non_neg
from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import SGD
from entities import LOCAL_TEAM, VISITOR_TEAM


class BestPlayerCalculator:
    EPOCHS_COUNT = 32

    def __init__(self, max_players_count):
        self.players = {}
        self.players_count = 0
        self.first_layer_size = max_players_count + 1

        self.model = Sequential()
        self.model.add(
            Dense(
                1,
                input_dim=self.first_layer_size,
                use_bias=False,
                kernel_constraint=non_neg(),
                activation='linear'
            )
        )

        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        self.model.compile(loss='mean_squared_error', optimizer=sgd)

    def add_fixtures(self, fixtures):
        prepared = []
        for fixture in fixtures:
            self._add_players(fixture.get_all_players())
            prepared += self._prepare_samples(fixture)

        n = len(prepared)

        x = np.empty((n, self.first_layer_size))
        y = np.empty((n,))

        for key, data in enumerate(prepared):
            x[key] = data['x']
            y[key] = data['y']

        self.model.fit(x, y, epochs=self.EPOCHS_COUNT, verbose=0)

    def get_top_players(self, count):
        players_list = list(self.players.values())

        weights = self.model.get_weights()[0]
        for key, player in enumerate(players_list):
            players_list[key].skill = weights.item((player.node_id,))

        players_list.sort(key=lambda p: p.skill, reverse=True)

        return players_list[:count]

    def _prepare_samples(self, fixture):
        # fixture.substitutions.sort(key=lambda s: s.minute)
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

            samples.append({'x': x, 'y': y, 'weight': weight})

        return samples

    def _calculate_x(self, fixture, sample_minute_from, sample_minute_to):
        if sample_minute_to < sample_minute_from:
            raise ValueError(
                "sample_minute_to can't be higher than sample_minute_from"
            )

        x = np.zeros((self.first_layer_size,))

        # Those two loops could be merged into one but this way the
        # time complexity is better (because otherwise you would have
        # to find out to which team the player belongs)
        for player in fixture.local_team_players:
            # @todo change to player.node_id
            node_id = self.players[player.id].node_id
            x[node_id] = self._get_node_activation(
                fixture,
                player,
                sample_minute_from,
                sample_minute_to,
                LOCAL_TEAM
            )
        for player in fixture.visitor_team_players:
            node_id = self.players[player.id].node_id
            x[node_id] = self._get_node_activation(
                fixture,
                player,
                sample_minute_from,
                sample_minute_to,
                VISITOR_TEAM
            )
        return x

    @staticmethod
    def _get_node_activation(
            fixture,
            player,
            sample_minute_from,
            sample_minute_to,
            team
    ):
        minutes_played = fixture.get_minutes_played(
            player,
            sample_minute_from,
            sample_minute_to
        )
        match_length = fixture.match_length
        # @todo change match_length to standard_match_length
        ratio = minutes_played / match_length
        return ratio if team == LOCAL_TEAM else -ratio

    def _calculate_y(self, fixture, sample_minute_from, sample_minute_to):
        result_before = fixture.get_result_in_minute(sample_minute_from)
        result_before = self._convert_result_to_int(
            result_before['local_team_score'],
            result_before['visitor_team_score']
        )
        result_after = fixture.get_result_in_minute(sample_minute_to)
        result_after = self._convert_result_to_int(
            result_after['local_team_score'],
            result_after['visitor_team_score']
        )
        return result_after - result_before

    @staticmethod
    def _calculate_weight(fixture, sample_minute_from, sample_minute_to):
        # @todo change match_length to standard_match_length
        return (sample_minute_to - sample_minute_from) / fixture.match_length

    @staticmethod
    def _convert_result_to_int(local_team_score, visitor_team_score):
        return 10 * (local_team_score - visitor_team_score)

    # @staticmethod
    # def _convert_result_to_int(local_team_score, visitor_team_score):
    #     if local_team_score > visitor_team_score:
    #         return (
    #             (local_team_score / visitor_team_score) - 1
    #             if visitor_team_score
    #             else local_team_score
    #         )
    #
    #     if visitor_team_score > local_team_score:
    #         return -(
    #             (visitor_team_score / local_team_score) + 1
    #             if local_team_score
    #             else visitor_team_score
    #         )
    #
    #     return 0

    def _add_players(self, players):
        for player in players:
            if player.id not in self.players:
                self.players[player.id] = player
                self.players[player.id].node_id = self.players_count
                self.players_count += 1

            # @todo: move to separate method
            if hasattr(self.players[player.id], 'occurrences'):
                self.players[player.id].occurrences += 1
            else:
                self.players[player.id].occurrences = 1
