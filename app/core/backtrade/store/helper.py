from datetime import datetime, timedelta

import backtrader as bt

from app.core.backtrade.params import BackTradeParamsUtil
from app.core.backtrade.store import CCXTStore


class CctxStoreHelper:
    @staticmethod
    def load_data(store, timeframe: str, symbol: str):
        compression, timeframe = BackTradeParamsUtil.parse_timeframe(timeframe)
        # Get our data
        # Drop newest will prevent us from loading partial data from incomplete candles
        hist_start_date = datetime.utcnow() - timedelta(minutes=60)
        klines = store.getdata(dataname=symbol, name=symbol,
                               timeframe=timeframe, fromdate=hist_start_date,
                               compression=compression, ohlcv_limit=50, drop_newest=True)
        return klines

    @staticmethod
    def instance_cerebro( strategy, currency: str = 'USDT',
                         sandbox=False):
        cerebro = bt.Cerebro(quicknotify=True)
        # Add the strategy
        cerebro.addstrategy(strategy)
        # Create our store
        config = {'apiKey': "KF1ELZxnpyCVjoV1TnagFqbr0dGaw2VvMwLylwVoUXU6bN7OPTASddFwyQWFNsnt",
                  'secret': "3f3Yaew7mWDJrZLcr5FQAYq4kdpqkgcsFL8MQQZRP6KB9SKOpexj1Ua7ahGKxSiJ",
                  'enableRateLimit': True,
                  }
        store = CCXTStore(exchange='binance', currency=currency, config=config, retries=5, debug=False)

        broker_mapping = {
            'order_types': {
                bt.Order.Market: 'market',
                bt.Order.Limit: 'limit',
                bt.Order.Stop: 'stop-loss',  # stop-loss for kraken, stop for bitmex
                bt.Order.StopLimit: 'stop limit'
            },
            'mappings': {
                'closed_order': {
                    'key': 'status',
                    'value': 'closed'
                },
                'canceled_order': {
                    'key': 'result',
                    'value': 1}
            }
        }
        broker = store.getbroker(broker_mapping=broker_mapping)
        cerebro.setbroker(broker)
        return cerebro, store
