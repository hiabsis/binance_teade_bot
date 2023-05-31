import datetime
import enum

import backtrader as bt
import pandas as pd
from loguru import logger

from app.core.config import Config
from app.core.utils.cctx import OhlvUtil

if Config.strategy_run_mod() == 'Debug':
    DEBUG = True
else:
    DEBUG = False


class OrderSide(enum.Enum):
    BUY = 1
    SELL = 2


class CoreStrategy(bt.Strategy):

    def __init__(self):

        self.live_data = False
        pass

    def log(self, txt, dt=None, doprint=False):
        """
        日志函数
        """
        if doprint or DEBUG:
            if dt is None:

                date_str = bt.num2date(self.datas[0].lines.datetime[0])
            else:
                date_str = bt.num2date(bt)
            logger.debug('%s, %s' % (date_str, txt))

    def get_position(self) -> float:
        return self.getposition(self.datas[0]).size

    @property
    def balance(self) -> float:
        """
        当前可用资金
        :return:
        """
        return self.broker.getvalue() - abs(self.position.size * self.position.price)


class CoreRunner:
    @staticmethod
    def load_data(runparams) -> pd.DataFrame:
        kines = OhlvUtil.load_ohlv_as_pd(symbol=runparams.symbol, timeframe=runparams.timeframe,
                                         start=runparams.start, end=runparams.end)
        return kines

    @staticmethod
    def run(runparams):
        pass


class StoreStrategy(CoreStrategy):

    def __init__(self):

        self.sma = bt.indicators.SMA(self.data, period=21)
        self.bought = False
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.dt = None

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
            self.log('{} balance {}'.format(symbol, self.balance))

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.datetime.now()
        msg = 'Data Status: {}'.format(data._getstatusname(status))
        self.log("feed data {} {} {} ".format(dt, dn, msg))
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False

    def notify_order(self, order):
        """
        订单状态处理

        """

        if order.status in [order.Submitted, order.Accepted]:
            # 如订单已被处理，则不用做任何事情
            return
        # 检查订单是否完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, 价格: %.2f, 花费: %.2f, 手续费 %.2f,数量 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     order.executed.size,), doprint=True)
            else:
                self.log('SELL EXECUTED, 价格: %.2f, 花费: %.2f, 手续费 %.2f 数量%.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm,
                          order.executed.size), doprint=True)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # 订单状态处理完成，设为空
        self.order = None
