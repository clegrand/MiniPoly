import random

import names
from math import ceil

from game.kitchen import StartCase, CashCase, District
from attic import START_CASH, DICE_RANGE, CASH_CASH, CASH_GAIN, DISTRICT_RANGE


class MetaPlan(type):
    def generate(cls, **kwargs):
        def generate_parks_index(plan_size, num=1, indexes_to_avoid=tuple()):
            range_available = list(range(plan_size))
            for index_to_avoid in indexes_to_avoid:
                range_available.pop(index_to_avoid)
            parks = []
            for _ in range(num):
                choose = random.choice(range_available)
                parks.append(choose)
                range_available.remove(choose)
            return parks

        players_base = kwargs.get('players_pos')
        players_start = kwargs.get('players')
        num_players = (len(players_base) if players_base is not None else 0) +\
                      (len(players_start) if players_start is not None else 0)
        if players_base is None and players_start is None:
            num_players = kwargs.get('players_num')
        size = kwargs.get('size')
        if size is None:
            if num_players is None:
                raise KeyError("missing 'size' or 'players_pos' or 'players_num' field")
            size = num_players * ceil(max(kwargs.get('dice_range', DICE_RANGE)) * 0.75)
        start_case = kwargs.get('start_index', 0)
        parks_case = kwargs.get(
            'cash_indexes',
            generate_parks_index(size, num_players - 1 if num_players is not None else 1, (start_case, ))
        )
        start_cash = kwargs.get('start_cash', START_CASH)
        parks_cash = kwargs.get('cash_cash', CASH_CASH)
        parks_gain = kwargs.get('cash_gain', CASH_GAIN)
        district_range = kwargs.get('district_range', DISTRICT_RANGE)
        plan = []
        for pos in range(size):
            if pos == start_case:
                case = StartCase(name=kwargs.get('start_name', 'Start'), cash=start_cash)
            elif pos in parks_case:
                case = CashCase('Park', cash=parks_cash, gain=parks_gain)
            else:
                case = District("{} district".format(names.get_full_name()),
                                price=random.randint(*district_range))
            plan.append(case)
        return cls(plan, **kwargs)
