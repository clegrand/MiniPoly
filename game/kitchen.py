import random

from itertools import chain


class Player:
    def __init__(self, name, money=0, districts=None):
        self.name = name
        self.money = money
        self.districts = DistrictManager(districts or tuple(), owner=self)

    def __call__(self):
        # TODO: Can improve districts
        self.cell_districts()
        return bool(self)

    def pay(self, to_pay, fatal=True):
        if isinstance(to_pay, District):
            price = to_pay.price
            if to_pay.owner is not None:
                to_pay.owner.money += price
        elif isinstance(to_pay, CashCase):
            price = to_pay.gain
        else:
            price = to_pay
        self._get_money(to_pay)
        if not fatal:
            price = min(self.money, price)
        self.money -= price
        return price

    def buy(self, to_buy):
        if self._validate(to_buy):
            self.pay(to_buy)
            if isinstance(to_buy, District):
                self.districts.add(to_buy)

    def cell_districts(self, target=None):
        for case in self._select_districts(kind='cell' if target is None else 'give', target=target):
            self.money += case.price
            self.districts.remove(case)

    # noinspection PyMethodMayBeStatic
    def launch_dice(self, dice_range):
        return random.randint(*dice_range)

    def _get_money(self, target=None):
        if target is None:
            price = 0
            target = None
        elif isinstance(target, District):
            price = target.price
            target = target.owner
        elif isinstance(target, CashCase):
            price = target.gain
            target = None
        else:
            price = target
            target = None
        while self.money < price:
            if not self.districts:
                break
            self.cell_districts(target)
        return self.money

    def _validate(self, to_validate):
        if isinstance(to_validate, District):
            price = to_validate.price
        else:
            price = to_validate
        if price >= self._total_cost():
            return False
        return True

    def _select_districts(self, kind=None, **kwargs):
        raise NotImplementedError

    def _total_cost(self):
        return sum((d.price for d in self.districts), self.money)

    def __str__(self):
        base_str = "{0.name} with {0.money}$".format(self)
        if self.districts:
            base_str = ' '.join((base_str, "and {}".format(self.districts)))
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

    def _add_owner(self, element):
        if isinstance(element.owner, Player):
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
        player.money += self.cash

    def _pick_cash(self, player):
        player.money += self.cash
        self.cash = 0

    def _gain(self, player):
        player.pay(self, fatal=False)
        self.cash += self.gain

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

    def __init__(self, name, price, owner=None):
        super().__init__(name)
        self.price = price
        self.owner = owner

    def __call__(self, player):
        if self.owner is None:
            player.buy(self)
        elif player is not self.owner:
            player.pay(self)

    def __str__(self):
        base_str = "{0.name}: {0.price}$".format(self)
        if self.owner is not None:
            base_str = ' '.join((base_str, "at '{}'".format(self.owner.name)))
        return base_str

    def __repr__(self):
        return "District {0.name} ({0.price}$)".format(self)
