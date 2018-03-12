LOCAL_TEAM = 0
VISITOR_TEAM = 1


class Player:
    def __init__(self, id, first_name=None, last_name=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

    def __str__(self):
        return (
            self.first_name + " " + self.last_name
            if self.first_name and self.last_name
            else self.id
        )

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.id == other.id


class Substitution:
    def __init__(self, player_in, player_out, minute, team):
        self.player_in = player_in
        self.player_out = player_out
        self.minute = minute
        self.team = team


class Goal:
    def __init__(self, team, minute):
        self.team = team
        self.minute = minute


class Fixture:
    def __init__(
            self,
            local_team_players,
            visitor_team_players,
            local_team_score,
            visitor_team_score,
            substitutions=None,
            goals=None,
            match_length=90
    ):
        self.local_team_players = local_team_players
        self.visitor_team_players = visitor_team_players
        self.local_team_score = local_team_score
        self.visitor_team_score = visitor_team_score
        self.substitutions = substitutions or []
        self.goals = goals
        self.match_length = match_length

        self._validate_substitutions()
        self._update_substitutes()
        self._update_minutes_in_and_out()

    def get_minutes_played(self, player, minute_from=0, minute_to=None):
        if minute_to is None:
            minute_to = self.match_length
        if minute_to < minute_from:
            raise ValueError("Minute from has to be lower than minute to.")

        if player.id in self.players_went_in:
            went_in = self.players_went_in[player.id]
            return minute_to - max(went_in, minute_from)
        if player.id in self.players_went_out:
            went_out = self.players_went_out[player.id]
            return min(went_out, minute_to) - minute_from
        return minute_to - minute_from

    def get_result_in_minute(self, minute):
        if self.goals is None:
            return (
                {"local_team_score": 0, "visitor_team_score": 0}
                if minute < self.match_length
                else {
                    "local_team_score": self.local_team_score,
                    "visitor_team_score": self.visitor_team_score
                }
            )

        self.goals.sort(key=lambda g: g.minute)
        local_team_score = 0
        visitor_team_score = 0
        for goal in self.goals:
            if minute < goal.minute:
                break
            if goal.team == LOCAL_TEAM:
                local_team_score += 1
            elif goal.team == VISITOR_TEAM:
                visitor_team_score += 1
        return {
            "local_team_score": local_team_score,
            "visitor_team_score": visitor_team_score
        }

    def get_all_players(self):
        return (
            self.local_team_players +
            self.local_team_substitutes +
            self.visitor_team_players +
            self.visitor_team_substitutes
        )

    def _update_substitutes(self):
        self.local_team_substitutes = []
        self.visitor_team_substitutes = []
        for substitution in self.substitutions:
            if substitution.team == LOCAL_TEAM:
                self.local_team_substitutes.append(substitution.player_in)
            elif substitution.team == VISITOR_TEAM:
                self.visitor_team_substitutes.append(substitution.player_in)

    def _update_minutes_in_and_out(self):
        self.players_went_in = {}
        self.players_went_out = {}
        for substitution in self.substitutions:
            minute = substitution.minute
            self.players_went_in[substitution.player_in.id] = minute
            self.players_went_out[substitution.player_out.id] = minute

    def _validate_substitutions(self):
        pass

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
