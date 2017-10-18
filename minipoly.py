import argparse
import logging

from game.kitchen import Player
from console import ConsoleGame


def get_args(args=None):
    parse = argparse.ArgumentParser()
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
    get_args()
    gm = ConsoleGame(ps)
    gm.prepare()
    gm()
