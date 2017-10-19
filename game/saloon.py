import logging

from game.kitchen import StartCase
from tools.meta import MetaPlan
from attic import DICE_RANGE, PLAYERS_CASH


class Plan(list, metaclass=MetaPlan):
    def __init__(self, *args, players=tuple(), players_pos=None, **kwargs):
        super(Plan, self).__init__(*args)
        self._players_pos = players_pos or {}
        self._start = kwargs.get('start_index', self._start_case())
        self.adds_player(players)

    def player_position(self, player):
        return self[self._players_pos[player]]

    def move(self, player, dist):
        for _ in range(dist):
            yield self._forward(player, 1)

    def go_to(self, player, index):
        self._players_pos[player] = index
        return self[index]

    def add_player(self, player, index=None):
        if index is None:
            index = self._start
        return self.go_to(player, index)

    def adds_player(self, players, index=None):
        for player in players:
            self.add_player(player, index)

    def _forward(self, player, fwd):
        player_pos = self._players_pos[player]
        return self.go_to(player, (player_pos + fwd) % len(self))

    def _start_case(self):
        for i, e in enumerate(self):
            if isinstance(e['case'], StartCase):
                return i
        return 0

    def __iter__(self):
        players_pos = {}
        for k, v in self._players_pos.items():
            pos = players_pos.setdefault(v, [])
            pos.append(k)
        for i, c in enumerate(super().__iter__()):
            yield {'case': c, 'players': players_pos.get(i, [])}

    def __str__(self):
        return ">".join(map(lambda x: "[{} ({})]".format(x['case'], len(x['players'])), self))

    def __repr__(self):
        return "Plan {} cases | {} players".format(len(self), len(self._players_pos))


class Game:
    MODES = (
        'normal',
        'survival',
        'one-shot'
    )

    def __init__(self, players=None, plan=None, mode=MODES[0], **kwargs):
        self.players = players or []
        self.plan = plan
        self.mode = mode if mode in self.MODES else self.MODES[0]
        self.dice_range = kwargs.get('dice_range', DICE_RANGE)
        self._end = False

    def prepare(self, **kwargs):
        if not self.plan:
            kwargs.setdefault('players', self.players)
            self.plan = Plan.generate(**kwargs)
        immunize = self.mode in ('normal', 'survival')
        if any((p.money <= 0 for p in self.players)):
            players_money = kwargs.get('players_cash', PLAYERS_CASH)
            for player in self.players:
                player.money = players_money
                player.immunize = immunize
        elif immunize:
            for player in self.players:
                player.immunize = immunize

    def __call__(self):
        logging.debug("Mode selected: %s", self.mode)
        logging.debug("Players: %s", ', '.join(map(repr, self.players)))
        logging.info("Map: %s", self.plan)
        while not self.end:
            self.turn()
        return self.result()

    def turn(self):
        for player in self._players_ready():
            self.player_turn(player)
            if self.end:
                break

    def player_turn(self, player):
        fwd = player.launch_dice(self.dice_range)
        cases = tuple(self.plan.move(player, fwd))
        for case in cases[:-1]:
            case.cross(player)
        cases[-1](player)
        player()

    def result(self):
        return sorted(self.players, key=lambda p: p.total, reverse=True)

    @property
    def end(self):
        if not self._end:
            if self.mode in ('normal', 'one-shot') and all(self.players)\
                    or self.mode == 'survival' and len(tuple(self._players_ready())) <= 1:
                self._end = True
        return self._end

    @end.setter
    def end(self, state):
        self._end = state

    def _players_ready(self):
        return filter(None, self.players)
