from typing import Dict, List

import backtrader as bt

from app.core.backtrade.mock.model import OrderParamsFactory
from trade.utils.colour import ColourTxtUtil


def operation_help_info() -> str:
    return "{} {}: Busy {}: Sell  {}:Account {}: Next".format(
        ColourTxtUtil.cyan('Command'),
        ColourTxtUtil.red("B"),
        ColourTxtUtil.red("S"),
        ColourTxtUtil.red("A"),
        ColourTxtUtil.red("N"),

    )


def format_order_info(symbol, order):
    return "{} {} {} ".format(ColourTxtUtil.green("订单"),
                              ColourTxtUtil.cyan(symbol),
                              order
                              )
    # return "{} {} {}: {} {}:{} {}：{}".format(ColourTxtUtil.green("订单"),
    #                                          ColourTxtUtil.cyan(symbol),
    #                                          ColourTxtUtil.blue("Size"),
    #                                          order.size,
    #                                          ColourTxtUtil.blue("Price"),
    #                                          order.price,
    #                                          ColourTxtUtil.blue("Side"),
    #                                          order.type,
    #                                          ColourTxtUtil.blue("Type"),
    #                                          order.getstatusname()
    #                                          )


def format_klines_str(klines, index=0):
    symbol = fetch_klines_name(klines)
    date_str = bt.num2date(klines.lines[6][0])
    return "{} {} {}: {} {}: {} {}: {} {}: {} {}: {} {}:{} {}：{} %".format(
        ColourTxtUtil.cyan("行情"),
        symbol,

        ColourTxtUtil.blue("Time"),
        date_str,
        ColourTxtUtil.blue("Open"),
        klines.open[index],
        ColourTxtUtil.blue("High"),
        klines.high[0],
        ColourTxtUtil.blue("Low"),
        klines.low[0],
        ColourTxtUtil.blue(
            "Close"),
        klines.close[0],
        ColourTxtUtil.blue(
            "Volume"),
        klines.volume[0],
        ColourTxtUtil.blue(
            "Change"),
        (klines.close[0] - klines.open[0]) / klines.open[0] * 100
    )


def fetch_klines_name(klines):
    symbol = klines._name
    return symbol


def compute_profit(position, price):
    if position.price > 0 and position.price > 0:
        return (price - position.price) / position.price * 100
    elif position.price > 0 and position.price > 0:
        return 0 - (abs(position.price) - price) / abs(position.price) * 100
    return 0


class SpotStrategy(bt.Strategy):
    logger = print

    def __init__(self):
        self.threshold = 0  # 设置阈值为 -1000.0，小于此值即控制账户负余额风险

        self.orders: Dict[str, List] = {}

        self.symbols = {}
        for klines in self.datas:
            self.orders[fetch_klines_name(klines)] = []
            self.symbols[fetch_klines_name(klines)] = klines

    def log(self, text):
        # date_str = bt.num2date(self.datas[0].lines[6][0])
        self.logger(text)

    def fetch_order_symbol(self, order):
        for symbol, orders in self.orders.items():
            for o in orders[:]:
                if o == order:
                    return symbol
        return None

    def notify_order(self, order):
        """
        订单状态处理

        """
        symbol = self.fetch_order_symbol(order)

        if order.status in [order.Submitted, order.Accepted]:
            # 如订单已被处理，则不用做任何事情
            return
            # 检查订单是否完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '%s: 执行做多, 价格: %.2f, 花费: %.2f, 手续费 %.2f,数量 %.2f' %
                    (ColourTxtUtil.blue(symbol),
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     order.executed.size,))
            else:
                self.log('%s: 执行做空, 价格: %.2f, 花费: %.2f, 手续费 %.2f 数量%.2f' %
                         (ColourTxtUtil.blue(symbol),
                          order.executed.price,
                          order.executed.value,
                          order.executed.comm,
                          order.executed.size))
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('{}: 订单取消、保证金不足、金额不足拒绝交易'.format(
                ColourTxtUtil.blue(symbol)
            ))
        elif order.status in [order.Expired]:
            self.log('{}: 超过时效，已取消'.format(
                ColourTxtUtil.blue(symbol)
            ))

        self.remove_order(order)

    def remove_order(self, order):
        for symbol, orders in self.orders.items():
            for o in orders[:]:
                if o == order:
                    orders.remove(o)

    def account_info(self):
        broker = self.broker

        return "{} {}: {} {}:{}".format(ColourTxtUtil.green("账户"),
                                        ColourTxtUtil.cyan("Assert"),
                                        broker.getvalue(),
                                        ColourTxtUtil.cyan("Clash"),
                                        broker.get_cash(),
                                        )

    def fetch_symbol_position(self, symbol):
        return self.getposition(self.symbols[symbol])

    def total_position_assert(self):
        value = 0
        for klines in self.datas:
            value += self.fetch_position_assert(klines)
        return value

    def fetch_position_assert(self, klines):
        position = self.getposition(klines)
        return position.size * position.price

    def show_position_info(self, klines):
        position = self.getposition(klines)
        symbol = fetch_klines_name(klines)

        self.log("{} {} {}: {} {}:{} {}：{} {}：{} %".format(ColourTxtUtil.green("资产"),
                                                           ColourTxtUtil.cyan(symbol),
                                                           ColourTxtUtil.blue("Size"),
                                                           position.size,
                                                           ColourTxtUtil.blue("Price"),
                                                           position.price,
                                                           ColourTxtUtil.blue("Assert"),
                                                           position.size * position.price,
                                                           ColourTxtUtil.blue("Profit"),
                                                           compute_profit(position, klines.close[0])
                                                           ))

    def show_order_info(self, klines):
        symbol = fetch_klines_name(klines)
        if symbol in self.orders:
            orders = self.orders[symbol]
            for order in orders:
                order_str = format_order_info(symbol, order)
                self.log(order_str)

    def show_klines_info(self, klines):
        self.log(format_klines_str(klines))

    def show_account_info(self):
        self.log(self.account_info())

    def notify_trade(self, trade):

        if not trade.isclosed:
            return

        self.log('{}: 净利润{} 净利润率{} %'.format(
            ColourTxtUtil.green("平仓"), round(trade.pnlcomm, 2), round(trade.pnlcomm, 2) / self.cash * 100))

    @property
    def cash(self):
        return self.broker.getvalue() - abs(self.total_position_assert())

    def next(self):
        # 交易信息
        self.log("\n{}".format(ColourTxtUtil.purple('实盘交易模拟器')))
        self.show_account_info()
        for klines in self.datas:
            self.show_position_info(klines)
            self.show_order_info(klines)
            self.show_klines_info(klines)
        # 从控制台获取指令
        self.input_command()
        pass

    def input_command(self):
        while True:
            self.log(operation_help_info())
            command = input("{}：".format(ColourTxtUtil.red("指令"))).replace(' ', '').upper()
            if command == '' or command == 'N':
                break
            elif command == 'A':
                self.show_account_info()
            elif command == 'B':
                self.execute_buy_command()
            elif command == 'S':
                self.execute_sell_command()

    def execute_sell_command(self):
        order = OrderParamsFactory.fetch_sell_by_console(self.log, list(self.symbols.keys()))
        # 检查是否有仓位
        position = self.fetch_symbol_position(order.symbol)
        if position.size == 0:
            self.log('{}: {}未持仓'.format(ColourTxtUtil.red('Error'), order.symbol))
            return
        size = position.size * order.ratio * 0.01
        klines = self.symbols[order.symbol]
        self.close(data=klines, size=size)

    def execute_buy_command(self):

        order = OrderParamsFactory.fetch_buy_by_console(self.log, list(self.symbols.keys()))
        klines = self.symbols[order.symbol]
        size = self.cash * 0.01 * order.ratio / klines.high[0]

        self.handle_order(order, size)

    def handle_order(self, order, size):
        klines = self.symbols[order.symbol]
        o = None
        self.log("{}: {}".format(ColourTxtUtil.orange("下单数量"), size))
        if order.type.is_market():

            if order.side.is_buy():
                o = self.buy(data=klines, size=size)
            elif order.side.is_sell():
                o = self.sell(data=klines, size=size)
        elif order.type.is_limit():
            if order.side.is_buy():
                o = self.buy(data=klines, size=size, price=order.price, exectype=bt.Order.Limit)
            elif order.side.is_sell():
                o = self.sell(data=klines, size=size, price=order.price, exectype=bt.Order.Limit)
        if o is not None:
            self.orders[order.symbol].append(o)
