import argparse
import logging

from game.saloon import Game
from console import ConsoleGame


def get_args(args=None):
    parse = argparse.ArgumentParser()
    parse.add_argument('-m', '--game-mode', metavar='MODE', default=Game.MODES[0], choices=Game.MODES,
                       help="select game mode")
    parse.add_argument('-d', '--debug', action='store_true',
                       help="increase debug mode")
    parsed = parse.parse_args(args)
    # TODO: Improve logging config
    if parsed.debug:
        logging.basicConfig(level='DEBUG')
    return parsed


if __name__ == '__main__':
    i = 1
    ps = []
    args = get_args()
    gm = ConsoleGame(ps, mode=args.game_mode)
    gm.prepare()
    gm()
