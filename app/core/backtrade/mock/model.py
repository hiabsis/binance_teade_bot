from datetime import datetime
from enum import Enum
from typing import List

from backtrader.feeds import PandasData
from loguru import logger

from app.core.config import BALANCE, FEE, SYMBOLS, TIMEFRAME, FROM_TIME, TO_TIME, ENABLE_SHORT
from app.core.utils.cctx import OhlvUtil
from app.core.utils.dateutil import DateUtil
from trade.utils.colour import ColourTxtUtil


class OrderSide(Enum):
    Buy = 'B'
    Sell = 'S'

    def is_buy(self) -> bool:
        return self.value == OrderSide.Buy.value

    def is_sell(self) -> bool:
        return self.value == OrderSide.Sell.value


class OrderType(Enum):
    Market = 'M'
    Limit = 'L'

    def is_market(self) -> bool:
        return self.value == OrderType.Market.value

    def is_limit(self) -> bool:
        return self.value == OrderType.Limit.value


class OrderParam:
    ratio: float
    price: float
    symbol: str
    side: OrderSide
    type: OrderType

    def __init__(self, log):
        self.log = log

    def is_limit(self) -> bool:
        return self.type == 'L'

    def is_market(self) -> bool:
        return self.type == 'M'

    def fetch_side(self):
        while True:
            self.log("{}:做多 {}：做空".format(ColourTxtUtil.red(OrderSide.Buy.value),
                                              ColourTxtUtil.red(OrderSide.Sell.value)))
            order_side = input("{}：".format(ColourTxtUtil.orange("订单方向："))).replace(' ', '').upper()

            if order_side == OrderSide.Sell.value:
                self.side = OrderSide.Sell
                break
            elif order_side == OrderSide.Buy.value:
                self.side = OrderSide.Buy
                break

    def fetch_type(self):
        while True:
            self.log("{}:市价 {}：限价".format(ColourTxtUtil.red(OrderType.Market.value),
                                              ColourTxtUtil.red(OrderType.Limit.value)))
            order_type = input("{}：".format(ColourTxtUtil.orange("订单类型："))).replace(' ', '').upper()

            if order_type == OrderType.Market.value:
                self.type = OrderType.Market
                break
            elif order_type == OrderType.Limit.value:
                self.type = OrderType.Limit
                break

    def fetch_symbol(self, symbols):
        while True:
            self.log("{}: {}".format(ColourTxtUtil.red("Symbols:"),
                                     symbols))
            symbol = input("{}：".format(ColourTxtUtil.orange("Symbol："))).replace(' ', '').upper()
            if symbol in symbols:
                self.symbol = symbol
                break
            else:
                self.log(ColourTxtUtil.red("{} not in  support symbols ".format(symbol)))

    def fetch_price(self):
        while True:
            price = input("{}：".format(ColourTxtUtil.orange("Price："))).replace(' ', '').lower()
            try:

                price = float(price)
            except ValueError:
                self.log(ColourTxtUtil.red('price must be float'))

            if 0 < price:
                self.price = price
                break
            else:
                self.log(ColourTxtUtil.red("price should be > 0"))

    def fetch_ratio(self):
        while True:
            self.log("{}: (0,100] %".format(ColourTxtUtil.red("开仓比列")))
            size_ratio = input("{}：".format(ColourTxtUtil.orange("Ratio："))).replace(' ',
                                                                                     '').lower()
            try:
                size_ratio = float(size_ratio)
            except ValueError:
                self.log(ColourTxtUtil.red('ratio must be float'))
                continue
            if 0 < size_ratio <= 100:
                self.ratio = size_ratio
                break
            else:
                self.log(ColourTxtUtil.red("ratio should be in (0,100]"))

    def fetch_params_by_console(self, symbols):
        self.fetch_side()
        self.fetch_type()
        self.fetch_symbol(symbols)
        self.fetch_ratio()

        if self.type.is_limit():
            self.fetch_price()


class OrderParamsFactory:

    @staticmethod
    def create_test_order_model(log, symbol: str) -> OrderParam:
        param = OrderParam(log=log)
        param.side = OrderSide.Sell
        param.type = OrderType.Market

        param.ratio = 100
        param.symbol = symbol.upper()
        return param

    @staticmethod
    def fetch_buy_by_console(log, symbols: list) -> OrderParam:
        params = OrderParam(log=log)
        params.side = OrderSide.Buy
        params.fetch_type()
        if len(symbols) == 1:
            params.symbol = symbols[0]
        else:
            params.fetch_symbol(symbols)
        params.fetch_ratio()

        if params.type.is_limit():
            params.fetch_price()
        return params

    @staticmethod
    def fetch_sell_by_console(log, symbols: list) -> OrderParam:
        params = OrderParam(log=log)
        params.side = OrderSide.Sell
        params.fetch_type()
        if len(symbols) == 1:
            params.symbol = symbols[0]
        else:
            params.fetch_symbol(symbols)
        params.fetch_ratio()

        if params.type.is_limit():
            params.fetch_price()
        return params


class RunParams:
    balance: float
    fee: float
    symbols: List = []
    timeframe: str = None
    from_time: datetime = None
    to_time: datetime = None
    enable_shore: bool = False

    def load_data(self) -> dict:
        klines = {}
        for symbol in self.symbols:
            klines[symbol] = OhlvUtil.load_ohlv_as_pd(symbol=symbol,
                                                      timeframe=self.timeframe,
                                                      start=self.from_time,
                                                      end=self.to_time)
        return klines


class RunParamsFactory:
    @staticmethod
    def load_by_config() -> RunParams:

        logger.debug("配置文件 ")
        logger.debug("BALANCE {}".format(BALANCE))
        logger.debug("FEE {}".format(FEE))
        logger.debug("SYMBOLS {}".format(SYMBOLS))
        logger.debug("TIMEFRAME {}".format(TIMEFRAME))
        logger.debug("FROM_TIME {}".format(FROM_TIME))
        logger.debug("TO_TIME {}".format(TO_TIME))
        logger.debug("ENABLE_SHORT {}".format(ENABLE_SHORT))
        params = RunParams()
        params.symbols = SYMBOLS
        params.timeframe = BALANCE
        params.timeframe = TIMEFRAME
        params.fee = FEE
        params.enable_shore = ENABLE_SHORT
        params.balance = BALANCE
        if 'None' != FROM_TIME:
            params.from_time = DateUtil.format_to_begin_datetime(FROM_TIME)
        if 'None' != TO_TIME:
            params.to_time = DateUtil.format_to_begin_datetime(TO_TIME)
        return params


class MockPd(PandasData):
    lines = ('b_break',)  # 要添加的线
    params = (
        ('b_break', -1),

    )
