


from typing import List

from munch import DefaultMunch


class Order:
    """
    订单
    """
    price = 0
    amount = 0

    def __init__(self, price, amount):
        self.price = price
        self.amount = amount


class SymbolCurrentPrice:
    """
    当前价格
    """

    def __init__(self, buy_price, sell_price, spread, exchange_id, symbol):
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.spread = spread
        self.exchange_id = exchange_id
        self.symbol = symbol


class OHLCV:
    timestamp: int = 0
    openPrice: int = 0
    highestPrice: int = 0
    lowestPrice: int = 0
    closePrice: int = 0
    volume: int = 0
    exchangeId: str = ""
    symbol = ""
    resp: dict = {}

    def __init__(self, timestamp, open_price, highest_price, lowest_price, close_price, volume, symbol, exchange_id,
                 resp: dict):
        self.symbol = symbol
        self.exchange_id = exchange_id
        self.volume = volume
        self.closePrice = close_price
        self.openPrice = open_price
        self.highestPrice = highest_price
        self.lowestPrice = lowest_price
        self.timestamp = timestamp
        self.resp = resp


class OrderBookStructure:
    """
    订单簿结构
    """
    symbol: str = None
    timestamp: int = 0
    datetime: int = 0
    nonce: int = 0
    bids: List[Order] = []
    asks: List[Order] = []
    resp: dict = {}
    exchange_id: str = ""

    def __init__(self, orderbook: dict):
        self.resp = orderbook
        self.decoder(orderbook)

    def decoder(self, orderbook: dict):
        self.symbol = orderbook['symbol']
        self.timestamp = orderbook['timestamp']
        self.nonce = orderbook['nonce']
        for ask in orderbook['asks']:
            order = Order(ask[0], ask[1])
            self.asks.append(order)
        for bid in orderbook['bids']:
            order = Order(bid[0], bid[1])
            self.bids.append(order)

    def get_bids(self) -> List:
        return self.bids


class TradFree:
    cost: float = 0
    currency: str = ""
    rate: float = 0


class Trade:
    resp = []
    exchange_id: str = ""
    info: str = ""
    id: str = ""
    timestamp: int = 0
    datetime: str = 0
    symbol: str = ""
    # 'market', 'limit'
    type: str = ""
    # 'buy' or 'sell'
    side: str = ""
    #  'taker' or 'maker'
    takerOrMaker: str
    price: float = 0
    amount: float = 0
    cost: float = 0
    fee: TradFree = {}
    fees: List[TradFree] = []

    def __init__(self, o: object, exchange_id=None, resp=None):
        self.symbol = o.symbol
        self.exchange_id = exchange_id
        self.resp = resp
        self.fee = o.fee
        self.fees = o.fees
        self.cost = o.cost
        self.amount = o.amount
        self.type = o.type
        self.side = o.side
        self.datetime = o.datetime
        self.timestamp = o.timestamp
        self.takerOrMaker = o.takerOrMaker
        self.id = o.id
        self.info = o.info
        self.price = o.price

    @staticmethod
    def decode(trade: dict):
        munch_object = DefaultMunch.fromDict(trade)
        return Trade(munch_object)


class Account:
    id: str = ''
    type: str = ''
    name: str = ''
    code: str = ''
    info: dict = {}
    resp: dict = {}
    exchange_id: str = ''

    def __init__(self, o: object):
        self.info = o.info
        self.code = o.code
        self.name = o.name
        self.type = o.type
        self.id = o.id

    @staticmethod
    def decode(account: dict):
        munch_object = DefaultMunch.fromDict(account)
        return Trade(munch_object)


class Balance:
    # 可以使用的资产数量
    free: float
    #
    asset: str
    # 已经使用的资产数量，
    locked: float


class BalanceResponse:
    makerCommission: float = 0
    takerCommission: float = 0
    buyerCommission: float = 0
    sellerCommission: float = 0
    commissionRates: dict = {}
    canTrade: bool
    canWithdraw: bool
    canDeposit: bool
    brokered: bool
    requireSelfTradePrevention: bool
    updateTime: int
    accountType: str
    balances: List[Balance]
    permissions: str = []
    free: float
    # 已经使用的资产数量
    used: float
    # 总资产数量
    total: float

    def __init__(self, o: object):
        self.permissions = o.permissions
        self.balances = o.balances
        self.accountType = o.accountType
        self.updateTime = o.updateTime
        self.requireSelfTradePrevention = o.requireSelfTradePrevention
        self.canDeposit = o.canDeposit
        self.canWithdraw = o.canWithdraw
        self.canTrade = o.canTrade
        self.commissionRates = o.commissionRates
        self.makerCommission = o.makerCommission
        self.takerCommission = o.takerCommission
        self.buyerCommission = o.buyerCommission

    @staticmethod
    def decode(balance: dict):
        munch_object = DefaultMunch.fromDict(balance['info'])
        resp = BalanceResponse(munch_object)
        resp.free = balance['free']
        resp.total = balance['total']
        resp.used = balance['used']
        return resp


class OrderResponse:
    resp: dict
    id: int
    clientOrderId: int
    price: float
    status: str

    type: str
    side: str

    amount: float
    cost: float
    average: float
    datetime: str
    timestamp: int
    resp: dict

    def __init__(self, o: object):
        self.id = o.id
        self.clientOrderId = o.clientOrderId
        self.price = o.price
        self.status = o.status
        self.side = o.side
        self.amount = o.amount
        self.cost = o.cost
        self.average = o.average
        self.datetime = o.datetime
        self.timestamp = o.timestamp

    @staticmethod
    def decode(order: dict):
        munch_object = DefaultMunch.fromDict(order)
        resp = OrderResponse(munch_object)
        resp.resp = order
        return resp
