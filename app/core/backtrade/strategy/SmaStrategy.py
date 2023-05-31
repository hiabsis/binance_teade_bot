import pandas as pd
from backtrader.feeds import PandasData

from app.core.backtrade.client import BackTradeClient
from app.core.backtrade.params import CoreRunParams
from app.core.backtrade.template import CoreStrategy, CoreRunner
from app.core.utils.cctx import OhlvUtil


class SmaStrategyPD(PandasData):
    pass


class SmaStrategyRunParams(CoreRunParams):

    def __init__(self, runparams=None):
        super().__init__(params=runparams)


class SmaStrategy(CoreStrategy):

    def __init__(self, runparams: SmaStrategyRunParams):
        super().__init__(run_mode=runparams.run_mode)

    def next(self):
        self.log("可用资金：{}".format(self.balance), doprint=True)


class SmaStrategyRunner(CoreRunner):

    @staticmethod
    def load_data(runparams: SmaStrategyRunParams):
        kines = OhlvUtil.load_ohlv_as_pd(symbol=runparams.symbol, timeframe=runparams.timeframe,
                                         start=runparams.start, end=runparams.end)
        return kines

    @staticmethod
    def run(runparams: SmaStrategyRunParams):
        cerebro = SmaStrategyRunner.build_cerebro(runparams)
        BackTradeClient.console_analyze(cerebro)

    @staticmethod
    def build_cerebro(runparams):
        kines = SmaStrategyRunner.load_data(runparams)
        kines['Time'] = pd.to_datetime(kines['Time'])
        kines.set_index('Time', inplace=True)
        data = SmaStrategyPD(dataname=kines)
        cerebro = BackTradeClient.default_cerebro()
        cerebro.adddata(data=data)
        cerebro.addstrategy(strategy=SmaStrategy, runparams=runparams)
        return cerebro
