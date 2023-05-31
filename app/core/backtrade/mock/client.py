import pandas as pd

from app.core.backtrade.client import BackTradeClient
from app.core.backtrade.mock.model import RunParamsFactory, MockPd
from app.core.backtrade.mock.strategry import SpotStrategy


class MockClient:

    @staticmethod
    def run():
        params = RunParamsFactory.load_by_config()
        klines = params.load_data()
        cerebro = BackTradeClient.default_cerebro(cash=params.balance, commission=params.fee,
                                                  enable_short=params.enable_shore)
        cerebro.addstrategy(strategy=SpotStrategy)

        for symbol, kline in klines.items():
            kline['Time'] = pd.to_datetime(kline['Time'])
            kline.set_index('Time', inplace=True)
            cerebro.adddata(data=MockPd(dataname=kline), name=symbol)

        BackTradeClient.console_analyze(cerebro)
