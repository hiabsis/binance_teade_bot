import sys
from configparser import ConfigParser
from datetime import datetime
from typing import List

import enums as enums
from loguru import logger

from app.core.utils.dateutil import DateUtil
from trade.utils.colour import ColourTxtUtil

config_filename = './config.ini'
config = ConfigParser()
# 项目根路径
config.read(config_filename)

BALANCE = float(config.get('app', 'balance'))
FEE = float(config.get('app', 'fee'))
SYMBOLS = config.get('trade', 'symbols').split(',')
TIMEFRAME = config.get('trade', 'timeframe')
FROM_TIME = config.get('trade', 'from_time')
TO_TIME = config.get('trade', 'to_time')


logger.debug("加载配置文件 ")
logger.debug("BALANCE {}".format(BALANCE))
logger.debug("SYMBOLS {}".format(SYMBOLS))
logger.debug("TIMEFRAME {}".format(TIMEFRAME))


class RunParams:
    symbols: List = []
    timeframe: str = None
    from_time: datetime = None
    to_time: datetime = None


class RunParamsFactory:
    @staticmethod
    def load_by_config() -> RunParams:
        params = RunParams()
        params.symbols = SYMBOLS
        params.timeframe = TIMEFRAME
        if 'None' != FROM_TIME:
            params.from_time = DateUtil.format_to_begin_datetime(FROM_TIME)
        if 'None' != TO_TIME:
            params.to_time = DateUtil.format_to_begin_datetime(TO_TIME)
        return params


class SideEnums(enums.Enum):
    Sell = -1
    Buy = 1


class Order:
    ID: str
    symbol: str
    price: float
    size: float
    side: int

    def __init__(self, ID: str, symbol: str, price: float, size: float, side: int):
        self.ID = ID
        self.symbol = symbol
        self.price = price
        self.size = size
        self.side = side

    def side_label(self) -> str:
        if self.side == 1:
            side = '做多'
        elif self.side == -1:
            side = '做空'
        elif self.side == 0:
            side = '平仓'
        else:
            side = '未知'
        return side

    def detail(self) -> str:
        side = self.side_label()
        return "\n{}:{} {}: {} {}: {}  {}: {} {}: {}\n".format(

            ColourTxtUtil.orange('Symbol'),
            self.symbol,
            ColourTxtUtil.orange('Side'),
            side,
            ColourTxtUtil.orange('Id'),
            self.ID,
            ColourTxtUtil.orange('Price'),
            self.price,
            ColourTxtUtil.orange('Size'),
            self.size
        )


class Position:
    size: float
    price: float
    side: int
    symbol: str

    def __init__(self, symbol, size, price, side):
        self.symbol = symbol
        self.size = size
        self.price = price
        self.side = side

    def detail(self) -> str:
        return "{}: {} {}: {} {}: {}\n".format(ColourTxtUtil.green("数量"), self.size,
                                               ColourTxtUtil.green("价格"), self.price,
                                               ColourTxtUtil.green("方向"), self.side)


class Account:
    balance = BALANCE
    b_position: Position = None
    s_position: Position = None
    orders: List[Order] = []

    def detail(self) -> str:
        txt = "{}: {} \n".format(ColourTxtUtil.green("余额"), self.balance)
        if self.position is not None:
            p_txt = self.position.detail()
        else:
            p_txt = ColourTxtUtil.red("None")
        txt += "{}: {} \n".format(ColourTxtUtil.green("仓位"), p_txt)
        txt += self.orders_detail()
        return txt

    def orders_detail(self, ):
        if len(self.orders) == 0:
            o_txt = ColourTxtUtil.red("None")
        else:
            o_txt = ""
            for order in self.orders:
                o_txt += order.detail()
        return "{}: {} ".format(ColourTxtUtil.green("订单"), o_txt)

    def append_order(self, order: Order):
        self.orders.append(order)
