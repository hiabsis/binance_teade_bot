import datetime

from backtrader import Order
from loguru import logger

from app.core.backtrade.template import StoreStrategy


class RBeakerStrategy(StoreStrategy):
    buy_price = {}

    def next_open(self):
        if self.live_data:
            cash, value = self.broker.get_wallet_balance('USDT')
        else:
            # Avoid checking the balance during a backfill. Otherwise, it will
            # Slow things down.
            cash = 'NA'
        for data in self.datas:
            self.dt = self.data1.lines.datetime.date(0),

            self.log('{} - {} | Cash {} | O: {} H: {} L: {} C: {} V:{} '.format(data.datetime.datetime(),
                                                                                data._name, cash, data.open[0],
                                                                                data.high[0], data.low[0],
                                                                                data.close[0], data.volume[0],
                                                                                ))

    def log(self, txt, dt=None, doprint=False):
        logger.info("{}".format(txt))

    def next(self):

        for data in self.datas:
            self.dt = data.datetime.datetime(),
            self.log('{} - {} | Open: {} High: {} Low: {} Close: {} Volume:{} '.format(data.datetime.datetime(),
                                                                                       data._name, data.open[0],
                                                                                       data.high[0], data.low[0],
                                                                                       data.close[0], data.volume[0],
                                                                                       ))
            self.trade(data, data._name)

    def trade(self, data, symbol):

        if self.live_data:
            position = self.broker.get_wallet_balance(symbol)
            self.log('symbol {} balance {} position {}'.format(symbol, self.balance, position))
            stop_loss_ratio = 0.02
            take_profit_ratio = stop_loss_ratio * 2
            close = data.close[0]
            high = data.high[0]
            # 前一日最高价
            ph = data.high[-1]
            # 前一日最滴价
            pl = data.low[-1]
            # 前一日收盘价
            pc = data.close[-1]
            low = data.low[0]
            pivot = (pc + pl + ph) / 3
            indicator = {'b_break': ph + 2 * (pivot - pl),
                         's_setup': pivot + (ph - pl),
                         's_enter': 2 * pivot - pl,
                         'b_enter': 2 * pivot - ph,
                         'b_setup': pivot - (ph - pl),
                         's_break': pl - 2 * (ph - pivot)}
            average = (data.high[0] + data.open[0] * 2 + data.low[0]) / 3
            buy_size = round(max(self.balance / close, 10 / close + 0.001), 5)
            if position > 0:
                position_price = self.buy_price[symbol]

                is_stop_loos = (close - position_price) / position_price > stop_loss_ratio
                is_task_profit = (position_price - close) / position_price > take_profit_ratio
                if is_task_profit or is_stop_loos:
                    self.close()

                if high > indicator["s_setup"] and average < indicator['s_enter']:
                    # 多头持仓,当日内最高价超过观察卖出价后，
                    # 盘中价格出现回落，且进一步跌破反转卖出价构成的支撑线时，
                    # 采取反转策略，即在该点位反手做空
                    self.log("多头持仓,当日内最高价超过观察卖出价后跌破反转卖出价")
                    self.close()
            elif position == 0:
                if buy_size * close > self.balance:
                    self.log("账户余额不足")
                    return
                if average > indicator['b_break']:
                    self.log("空仓,盘中价格超过突破买入价: 开仓做多", doprint=True)

                    self.buy(data=data, size=buy_size, exectype=Order.Market)
                    self.buy_price[symbol] = close
                elif low < indicator['b_setup'] and average > indicator['b_enter']:
                    # 空头持仓，当日内最低价低于观察买入价后，
                    # 盘中价格出现反弹，且进一步超过反转买入价构成的阻力线时，
                    # 采取反转策略，即在该点位反手做多
                    self.log("空头持仓,当日最低价低于观察买入价后超过反转买入价: 反手做多", doprint=True)

                    self.buy(data=data, size=buy_size, exectype=Order.Market)
                    self.buy_price[symbol] = close

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.datetime.now()
        msg = 'Data Status: {}'.format(data._getstatusname(status))
        self.log("feed data {} {} {} ".format(dt, dn, msg))
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False
