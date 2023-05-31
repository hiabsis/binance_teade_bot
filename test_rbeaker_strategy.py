from loguru import logger

from app.core.backtrade.store.helper import CctxStoreHelper
from app.strategy.rbreaker import RBeakerStrategy


class RunParams:
    symbols = ['ETHUSDT']
    timeframe = '15m'
    strategy = RBeakerStrategy
    currency = 'USDT'


logger.debug("{} {} {}".format(RunParams.strategy, RunParams.timeframe, RunParams.symbols, ))
cerebro, store = CctxStoreHelper.instance_cerebro(strategy=RunParams.strategy, currency=RunParams.currency,
                                                  )
for symbol in RunParams.symbols:
    klines = CctxStoreHelper.load_data(store, RunParams.timeframe, symbol)
    cerebro.adddata(klines)
cerebro.run()
