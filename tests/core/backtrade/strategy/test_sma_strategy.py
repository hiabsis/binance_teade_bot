import unittest

from app.core.backtrade.client import StoreClient
from app.core.backtrade.strategy.SmaStrategy import SmaStrategyRunner, SmaStrategyRunParams, SmaStrategy

runparams = SmaStrategyRunParams()
runparams.symbol = "ETHUSDT"
runparams.timeframe = "1d"


class Test(unittest.TestCase):
    def test_run_sma_strategy(self):
        SmaStrategyRunner.run(runparams)

    def test_store(self):
        StoreClient.run(SmaStrategy)
