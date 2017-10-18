from game.kitchen import Player, District, CashCase
from tools.console import validate, select, put_message


class ConsolePlayer(Player):
    def pay(self, to_pay, fatal=True):
        if isinstance(to_pay, District):
            if to_pay.owner is not None and to_pay.owner is not self:
                put_message("You need to pay {0.price} to '{0.owner.name}'".format(to_pay))
        elif isinstance(to_pay, CashCase):
            put_message("You do contribute {0.gain} (next {1})".format(to_pay, to_pay.cash + to_pay.gain))
        return super().pay(to_pay, fatal)

    def _validate(self, to_validate):
        if super()._validate(to_validate):
            if isinstance(to_validate, District):
                return validate("Do you want to buy '{0.name}' for {0.price}?".format(to_validate))
            return validate()
        return False

    def _select_districts(self, kind=None, **kwargs):
        return select(self.districts)

