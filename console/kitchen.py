from game.kitchen import Player, District, CashCase
from tools.console import validate, select, put_message


class ConsolePlayer(Player):
    def won(self, money, source=None):
        if isinstance(source, CashCase):
            put_message("Congratulation ! You won {}$".format(money))
        super().won(money, source)

    def pay(self, price, to_pay=None, fatal=True):
        if isinstance(to_pay, Player):
            put_message("You need to pay {price}$ to '{player.name}'".format(price=price, player=to_pay))
        elif isinstance(to_pay, District):
            pass
        elif isinstance(to_pay, CashCase):
            put_message("You do contribute {price}$ (next {cash}$)".format(price=price, cash=to_pay.cash + to_pay.gain))
        else:
            put_message("You need to pay {price}$ for {target}".format(price=price, target=to_pay))
        return super().pay(price, to_pay, fatal)

    def _validate(self, price, to_validate=None):
        if super()._validate(price, to_validate):
            if isinstance(to_validate, District):
                return validate("Do you want to buy '{0.name}' for {0.price}$ ?".format(to_validate))
            return validate()
        put_message("You don't have enough cash for buy {} (missing {}$)".format(to_validate, price - self.total))
        return False

    def _select_districts(self, kind=None, **kwargs):
        return select(self.districts)
