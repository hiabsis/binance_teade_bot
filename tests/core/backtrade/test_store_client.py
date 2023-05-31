from app.core.backtrade.client import BackTradeClient
from app.core.backtrade.template import StoreStrategy


class TestStrategy(StoreStrategy):
    pass


BackTradeClient.run(strategy=TestStrategy)
