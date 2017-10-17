import random

FIRST_MONEY = 8000
PRICE_RANGE = 50, 3000
PLAN_RANGE = 8, 18


class Player:
    def __init__(self, name, cost=0):
        self.name = name
        self.cost = cost


class Case:
    def __init__(self, price, owner=None):
        self.price = price
        self.owner = owner


class Game:
    DICE_RANGE = (1, 6)

    def __init__(self, players, plan, **kwargs):
        self.players = players
        for player in filter(lambda p: p.cost <= 0, players):
            player.cost = kwargs.get('money', FIRST_MONEY)
        self.plan = plan
        self._players_plan = dict.fromkeys(players, 0)
        self.end = False

    def __call__(self):
        while not self.end:
            self.turn()
        return self.result()

    def turn(self):
        for player in ps:
            self.player_turn(player)
            if self.end:
                break

    def player_turn(self, player):
        self.run(player)
        self.manage(player)
        self.check(player)
        if self._is_player_lose(player):
            self.player_lose(player)

    def run(self, player):
        pos = self._players_plan[player] + random.randint(*self.DICE_RANGE)
        l = len(self.plan)
        min_ = min(PRICE_RANGE)
        player.cost += ((max(PRICE_RANGE) - min_) / 2 + min_) * (pos // l)
        pos %= l
        self._players_plan[player] = pos
        return pos

    def manage(self, player):
        case = self.plan[self._players_plan[player]]
        if case.owner is None:
            self._buy_case(player, case)
        elif case.owner is not player:
            self._pay_case(player, case)

    def check(self, player):
        while True:
            cases = tuple(self._get_cases(player))
            if not self._is_player_lose(player) or not cases:
                break
            self._sale_case(self._select_case(list(cases)))

    def result(self):
        raise NotImplementedError

    def player_lose(self, player):
        self.end = True

    def _buy_case(self, player, case):
        if self._is_buy_case(player, case):
            player.cost -= case.price
            case.owner = player

    def _pay_case(self, player, case):
        player.cost -= case.price
        case.owner.cost += case.price

    @staticmethod
    def _sale_case(case):
        case.owner.cost += case.price
        case.owner = None

    def _is_buy_case(self, player, case):
        raise NotImplementedError

    def _is_player_lose(self, player):
        return player.cost < 0

    def _get_cases(self, search):
        return filter(lambda x: x.owner is search, self.plan)


class ConsoleGame(Game):
    def player_turn(self, player):
        print("\nIt's your turn {0.name}: {0.cost}".format(player))
        super().player_turn(player)

    def run(self, player):
        new_pos = super().run(player)
        case = self.plan[self._players_plan[player]]
        print(
            "You are in the case of {} and her price is {}".format(
                "'nobody'" if case.owner is None else case.owner.name,
                case.price
            )
        )
        return new_pos

    def result(self):
        players = sorted(self.players, key=lambda x: x.cost, reverse=True)
        print("The classification:\n{}".format(
            '\n'.join(
                ("{} - {}: {}{}".format(
                    i,
                    p.name,
                    p.cost,
                    " WIN" if i <= 1 else ""
                )
                    for i, p in enumerate(players, 1))
            )
        )
        )
        return players[0]

    def player_lose(self, player):
        print("Player {} has lose".format(player.name))
        super().player_lose(player)

    def _select_case(self, cases):
        print("Select a case:\n{}".format(
            '\n'.join(
                ("{} - {}".format(i, c.price)
                 for i, c in enumerate(cases, 1))
            )
        )
        )
        while True:
            try:
                c = int(input("> ")) - 1
            except (EOFError, ValueError):
                pass
            except KeyboardInterrupt:
                exit(0)
            else:
                try:
                    return cases[c]
                except IndexError:
                    pass

    def _is_buy_case(self, player, case):
        if player.cost >= case.price:
            print("Do you want to buy this case?"
                  .format(player.name, player.cost, case.price))
            try:
                r = input("> ")
                if r.lower() in ("y", "yes"):
                    return True
            except EOFError:
                pass
            except KeyboardInterrupt:
                exit(0)
        return False


if __name__ == '__main__':
    i = 1
    ps = []
    while True:
        try:
            p = input("Player {} name: ".format(i))
            if not p:
                break
            ps.append(Player(p))
        except EOFError:
            break
        except KeyboardInterrupt:
            exit(0)
        i += 1
    tabs = [Case(random.randint(*PRICE_RANGE))
            for _ in range(random.randint(*PLAN_RANGE))]
    gm = ConsoleGame(ps, tabs)
    gm()
