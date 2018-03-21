LOCAL_TEAM = 0
VISITOR_TEAM = 1


class Player:
    def __init__(self, id, first_name=None, last_name=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return (
            self.first_name + " " + self.last_name
            if self.first_name and self.last_name
            else str(self.id)
        )

    def __eq__(self, other):
        return self.id == other.id


class Substitution:
    def __init__(self, player_in, player_out, minute, team):
        self.player_in = player_in
        self.player_out = player_out
        self.minute = minute
        self.team = team

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)


class Goal:
    def __init__(self, team, minute):
        self.team = team
        self.minute = minute

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)


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

        self.substitutions.sort(key=lambda s: s.minute)
        self.goals.sort(key=lambda g: g.minute)

        self._validate_substitutions()
        self._update_substitutes()
        self._update_minutes_in_and_out()
        self._update_match_length()

        self._validate_goals()

    def get_minutes_played(self, player, minute_from=0, minute_to=None):
        if minute_to is None:
            minute_to = self.match_length
        if minute_to < minute_from:
            raise ValueError("minute_to can't be higher than minute_from")

        # @todo the player who came in can be changed as well
        if player.id in self.players_came_in:
            came_in = self.players_came_in[player.id]
            return minute_to - max(came_in, minute_from)
        if player.id in self.players_came_out:
            came_out = self.players_came_out[player.id]
            return min(came_out, minute_to) - minute_from
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

        # @todo sort it only once
        score = {LOCAL_TEAM: 0, VISITOR_TEAM: 0}
        for goal in self.goals:
            if minute < goal.minute:
                break
            if goal.team == LOCAL_TEAM:
                score[LOCAL_TEAM] += 1
            elif goal.team == VISITOR_TEAM:
                score[VISITOR_TEAM] += 1
        # @todo change to using LOCAL_TEAM and VISITOR_TEAM constants
        return {
            "local_team_score": score[LOCAL_TEAM],
            "visitor_team_score": score[VISITOR_TEAM]
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
        self.players_came_in = {}
        self.players_came_out = {}
        for substitution in self.substitutions:
            minute = substitution.minute
            self.players_came_in[substitution.player_in.id] = minute
            self.players_came_out[substitution.player_out.id] = minute

    def _update_match_length(self):
        last_substitution_minute = (
            self.substitutions[-1].minute
            if self.substitutions
            else 0
        )
        last_goal_minute = (
            self.goals[-1].minute
            if self.goals
            else 0
        )
        if self.match_length is None:
            self.match_length = 90
        self.match_length = max(
            self.match_length,
            last_substitution_minute,
            last_goal_minute
        )

    def _validate_substitutions(self):
        pass

    def _validate_goals(self):
        pass

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)
