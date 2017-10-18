from itertools import count

from game.saloon import Game
from console.kitchen import ConsolePlayer
from attic import PLAYERS_CASH


class ConsoleGame(Game):
    def prepare(self, **kwargs):
        if not self.players:
            for i in count(1):
                try:
                    p = input("Player {} name: ".format(i))
                    if not p:
                        break
                    self.players.append(ConsolePlayer(p))
                except EOFError:
                    break
        kwargs.setdefault('players_num', len(self.players))
        kwargs.setdefault('players_cash', PLAYERS_CASH)
        super().prepare(**kwargs)

    def player_turn(self, player):
        print("\nIt's your turn {}".format(player))
        super().player_turn(player)

    def result(self):
        players = sorted(self.players, key=lambda x: x.money, reverse=True)
        print("The classification:\n{}".format(
            '\n'.join(
                ("{} - {}: {}{}".format(
                    i,
                    p.name,
                    p.money,
                    " WIN" if i <= 1 else ""
                )
                    for i, p in enumerate(players, 1))
            )
        )
        )
        return players[0]