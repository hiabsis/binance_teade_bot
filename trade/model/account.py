from typing import List

from trade.core.config import BALANCE, FEE
from trade.model.order import Order
from trade.model.position import Position
from trade.utils.colour import ColourTxtUtil


class Account:
    balance: float
    buy_positions: dict[str, Position] = {}
    sell_positions: dict[str, Position] = {}
    create_order: dict[str, List[Order]] = {}
    close_position_orders: dict[str, List[Order]] = {}
    fee: float = 0

    def format_str(self) -> str:
        txt = "{}: {} \n".format(ColourTxtUtil.green("余额"), self.balance)
        txt += self.position_info()
        txt += self.order_info()
        return txt

    def order_info(self) -> str:
        order_txt = '订单：'
        for key, value in self.create_order:
            for order in value:
                order_txt += order.format_str()
        order_txt = ''
        for key, value in self.close_position_orders:
            for order in value:
                order_txt += order.format_str()

        if order_txt == '平仓: ':
            order_txt = 'None\n'
        return "{} \n{}".format(ColourTxtUtil.green('订单'), order_txt)

    def position_info(self) -> str:
        p_txt = ''
        for key, value in self.buy_positions:
            p_txt += value.format_str()
        for key, value in self.sell_positions:
            p_txt += value.format_str()

        if p_txt == '':
            p_txt = 'None\n'
        return "{} \n{}".format(ColourTxtUtil.green('仓位'), p_txt)


class AccountFactory:

    @staticmethod
    def load_by_config() -> Account:
        account = Account()
        account.balance = BALANCE
        account.fee = FEE
        return account
