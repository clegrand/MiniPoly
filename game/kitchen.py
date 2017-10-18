import random
from collections import namedtuple

from itertools import chain

from attic import IMPROVE_POINT, IMPROVE_PRICE_COEFFICIENT, IMPROVE_COEFFICIENT, DICE_BONUS


class Player:
    def __init__(self, name, money=0, districts=None):
        self.name = name
        self.money = money
        self.districts = DistrictManager(districts or tuple(), owner=self)

    def __call__(self):
        self.manage_districts()
        return bool(self)

    def pay(self, price, to_pay=None, fatal=True):
        self._get_money(price, to_pay)
        if not fatal:
            price = min(self.money, price)
        self.money -= price
        return price

    def buy(self, price, to_buy=None):
        if self._validate(price, to_buy):
            if isinstance(to_buy, District):
                self.districts.add(to_buy)
            return price
        return None

    def won(self, money, source=None):
        self.money += money

    def manage_districts(self):
        improve_point = IMPROVE_POINT
        while improve_point:
            districts = list(self._select_districts(self.districts.improvable()))
            if not districts:
                break
            for district in districts:
                if improve_point:
                    district.improve()
                    improve_point -= 1

    def cell_districts(self, target=None):
        cases = self._select_districts()
        for case in cases:
            case.cell()
        return cases

    # noinspection PyMethodMayBeStatic
    def launch_dice(self, dice_range):
        result = random.randint(*dice_range)
        if result == max(*dice_range):
            self.won(DICE_BONUS)
        return result

    def _get_money(self, price=0, target=None):
        last_money = self.money
        while self.money < price:
            if not self.districts:
                break
            self.cell_districts(target)
        return self.money - last_money

    def _validate(self, price, to_validate=None):
        if price <= self.total:
            return True
        return False

    def _select_districts(self, districts=None):
        raise NotImplementedError

    @property
    def total(self):
        return self.money + self.districts.total

    def __str__(self):
        base_str = "{0.name} with {0.money}$".format(self)
        if self.districts:
            base_str = ' '.join((base_str, "and {0!r} for {0.total}$".format(self.districts)))
        return base_str

    def __repr__(self):
        return "Player {0.name} ({0.money}$) +[{1!r}]".format(self, self.districts)

    def __bool__(self):
        return self.money >= 0


class DistrictManager(set):
    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner

    def add(self, element):
        super().add(element)
        self._add_owner(element)

    def update(self, *s):
        elements = tuple(chain(*s))
        super().update(elements)
        for element in elements:
            self._add_owner(element)

    def cell(self, element):
        self.remove(element)
        element.owner.money += element.price

    def pop(self):
        element = super().pop()
        self._del_owner(element)

    def remove(self, element):
        super().remove(element)
        self._del_owner(element)

    def discard(self, element):
        super().discard(element)
        if element.owner is self.owner:
            self._del_owner(element)

    def clear(self):
        for element in self:
            self._del_owner(element)
        super().clear()

    def improvable(self):
        return filter(lambda d: d.current_improve, self)

    @property
    def total(self):
        return sum((d.price for d in self))

    def _add_owner(self, element):
        if isinstance(element.owner, Player) and element.owner is not self.owner:
            element.owner.districts.remove(element)
        element.owner = self.owner

    @staticmethod
    def _del_owner(element):
        element.owner = None

    def __str__(self):
        return "".join(map(lambda x: "[{}]".format(x), self)) or "[]"

    def __repr__(self):
        ld = len(self)
        return "{} {}".format(ld, "district" if ld <= 1 else "districts")


class Case:
    def __init__(self, name):
        self.name = name

    def __call__(self, player):
        raise NotImplementedError

    def cross(self, player):
        pass

    def __repr__(self):
        return "{0.__class__.__name__} {0.name}".format(self)


class CashCase(Case):
    def __init__(self, name, cash=0, gain=0):
        super().__init__(name)
        self.cash = cash
        self.gain = gain

    def __call__(self, player):
        self._pick_cash(player)

    def cross(self, player):
        self._gain(player)

    def _give_cash(self, player):
        player.won(self.cash, source=self)

    def _pick_cash(self, player):
        self._give_cash(player)
        self.cash = 0

    def _gain(self, player):
        self.cash += player.pay(self.gain, to_pay=self, fatal=False)

    def __str__(self):
        return "Gain: {0.cash}$ ({0.gain}$)".format(self)

    def __repr__(self):
        return "Cash {0.cash}$ ({0.gain}$)".format(self)


class StartCase(CashCase):
    def __init__(self, name, cash):
        super().__init__(name, cash)

    def __call__(self, player):
        self._give_cash(player)

    def cross(self, player):
        self._give_cash(player)

    def __str__(self):
        return "Start: {0.cash}$".format(self)

    def __repr__(self):
        return "Start ({0.cash}$)".format(self)


class District(Case):
    ImproveCheck = namedtuple('ImproveCheck', ('pay', 'next'))

    def __init__(self, name, price, improve_step=None, owner=None):
        super().__init__(name)
        self.price = price
        self.improve_state = iter(improve_step if improve_step is not None else self._next_improve())
        self.current_improve = None
        self._shift_improve()
        if price is None:
            self.price = self.current_improve[0]
            self._shift_improve()
        self.owner = owner

    def __call__(self, player):
        if self.owner is None:
            self._buy(player)
        elif player is not self.owner:
            self._pay(player)

    def improve(self):
        if self.current_improve is not None:
            if self.owner.buy(self.current_improve.pay, to_buy=self):
                self.owner.pay(self.current_improve.pay, to_pay=self)
                self.price = self.current_improve.next
                self._shift_improve()
            return True
        return False

    def cell(self):
        self.owner.won(self.price, source=self)
        self.owner.districts.remove(self)

    def _pay(self, player):
        self.owner.won(player.pay(self.price, to_pay=self.owner), source=player)

    def _buy(self, player):
        money = player.buy(self.price, to_buy=self)
        if money is not None:
            player.pay(money, to_pay=self)

    def _next_improve(self):
        while True:
            yield self.price * IMPROVE_PRICE_COEFFICIENT, self.price * IMPROVE_COEFFICIENT

    def _shift_improve(self):
        try:
            self.current_improve = next(self.improve_state)
            self.current_improve = self.ImproveCheck(
                pay=round(self.current_improve[0], 2),
                next=round(self.current_improve[1], 2)
            )
        except StopIteration:
            self.current_improve = None
        return self.current_improve

    def __str__(self):
        base_str = "{0.name}: {0.price}$".format(self)
        if self.owner is not None:
            base_str = ' '.join((base_str, "at '{}'".format(self.owner.name)))
        return base_str

    def __repr__(self):
        return "District {0.name} ({0.price}$)".format(self)
