import time
from typing import List

import ccxt

from loguru import logger

from app.core.cctx.model import OrderBookStructure, SymbolCurrentPrice, Trade, Account, BalanceResponse, OrderResponse, \
    OHLCV
from app.core.config import Config
from app.core.utils.dateutil import DateUtil

config = {
    'apiKey': Config.ccxt_api_key(),
    'secret': Config.cctx_secret(),
    'enableRateLimit': True,
    'nonce': lambda: str(int(time.time() * 1000)),
}

client = ccxt.binance(config)
# 沙盒模拟
# exchange.set_sandbox_mode(True)
# 限制下载速度
client.enableRateLimit = True


class ExchangeFactory:
    @staticmethod
    def get_exchange():
        return client

    @staticmethod
    def get_config() -> dict:
        return config


class CCtxAdapter:

    @staticmethod
    def fetch_order_book(symbol: str, limit=None, params=None) -> OrderBookStructure:
        if params is None:
            params = {''}
        orderbook = ExchangeFactory.get_exchange().fetch_order_book(symbol, limit, params=params)
        response = OrderBookStructure(orderbook)
        response.exchange_id = ExchangeFactory.get_exchange().id
        return response

    @staticmethod
    def fetch_order_book_l2(symbol: str, limit=None, params=None) -> OrderBookStructure:
        if params is None:
            params = {}
        orderbook = ExchangeFactory.get_exchange().fetch_l2_order_book(symbol, limit, params=params)
        response = OrderBookStructure(orderbook)
        response.exchange_id = ExchangeFactory.get_exchange().id
        return response

    @staticmethod
    def fetch_order_book_l1(symbol: str, limit=None, params=None) -> OrderBookStructure:
        if params is None:
            params = {}
        orderbook = ExchangeFactory.get_exchange().order
        response = OrderBookStructure(orderbook)
        response.exchange_id = ExchangeFactory.get_exchange().id
        return response

    @staticmethod
    def fetch_current_price(symbol: str) -> SymbolCurrentPrice:
        exchange = ExchangeFactory.get_exchange()
        orderbook = exchange.fetch_order_book(symbol)
        bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        return SymbolCurrentPrice(ask, bid, spread, exchange.id, symbol)

    @staticmethod
    def fetch_ohlcv(symbol: str, timeframe='1m', since=None, limit=None, params=None) -> List[OHLCV]:
        """

        :param symbol:
        :param timeframe:
        :param since:
        :param limit:
        :param params: 'mark'（标记） 'index'(指标) 'premiumIndex'（溢价指数）
        :return:
        """
        if params is None:
            params = {}
        resp = []
        ohlcv = ExchangeFactory.get_exchange().fetch_mark_ohlcv(symbol, timeframe, since, limit, params)

        for oh in ohlcv:
            resp.append(OHLCV(oh[0], oh[1], oh[2], oh[3], oh[4], oh[5], ExchangeFactory.get_exchange().id, symbol, oh))
        return resp

    @staticmethod
    def fetch_trades(symbol, since=None, limit=None, params=None) -> List[Trade]:
        resp = []
        if params is None:
            params = {}
        trades = ExchangeFactory.get_exchange().fetch_trades(symbol, since, limit, params)
        for trade in trades:
            t = Trade.decode(trade)
            t.exchange_id = ExchangeFactory.get_exchange().id
            t.resp = trade
            resp.append(t)
        return resp

    @staticmethod
    def query_user_account() -> List[Account]:
        resp = []
        accounts = ExchangeFactory.get_exchange().account()
        time.sleep(2)
        for account in accounts:
            account_decode = Account.decode(account)
            account_decode.exchange_id = ExchangeFactory.get_exchange().id
            account_decode.resp = account
            resp.append(account_decode)

        return resp

    @staticmethod
    def fetch_balance() -> BalanceResponse:
        balance_resp = ExchangeFactory.get_exchange().fetch_balance()
        return BalanceResponse.decode(balance_resp)

    @staticmethod
    def fetch_orders(symbol: str = None, since: int = None, limit: int = None, params: dict = None) -> OrderResponse:
        if params is None:
            params = {}
        order_resp = ExchangeFactory.get_exchange().fetch_orders(symbol, since, limit, params)
        return OrderResponse.decode(order_resp)

    @staticmethod
    def create_market_buy_order(symbol: str, amount: float):

        order_info = ExchangeFactory.get_exchange().create_market_buy_order(symbol, amount)
        pass

    @staticmethod
    def create_market_sell_order(symbol: str, amount, price):

        order_info = ExchangeFactory.get_exchange().create_market_sell_order(symbol, amount)
        pass

    @staticmethod
    def query_begin_timestamp(symbol: str) -> int:
        start_time = '2010-01-01 08:00:00'
        fmt = '%Y-%m-%d %H:%M:%S'
        time_array = time.strptime(start_time, fmt)
        timestamp = int(time.mktime(time_array)) * 1000
        params = {
            "startTime": timestamp
        }
        ohlcv = CCtxAdapter.fetch_ohlcv(symbol=symbol, timeframe='1d', params=params, limit=1)

        start_time = DateUtil.timestamp_to_format(ohlcv[0].timestamp / 1000)
        logger.debug("symbol {} start_time {}".format(symbol, start_time))

        return ohlcv[0].timestamp
