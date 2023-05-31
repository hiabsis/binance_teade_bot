from loguru import logger

from app.core.backtrade.store.helper import CctxStoreHelper
from app.core.backtrade.template import StoreStrategy


class RunParams:
    symbols = ['ETHUSDT']
    timeframe = '1m'
    strategy = StoreStrategy
    currency = 'USDT'


logger.debug("开始实盘测试: \n{} \n{}\n {}\n".format(RunParams.strategy, RunParams.timeframe, RunParams.symbols, ))
cerebro, store = CctxStoreHelper.instance_cerebro(strategy=RunParams.strategy, currency=RunParams.currency,
                                                  )
for symbol in RunParams.symbols:
    klines = CctxStoreHelper.load_data(store, RunParams.timeframe, symbol)
    cerebro.adddata(klines)
cerebro.run()
