import random

from kitchen import Player, Case
from saloon import ConsoleGame, PRICE_RANGE

PLAN_RANGE = 8, 18


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
