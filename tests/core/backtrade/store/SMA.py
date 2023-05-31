# from datetime import datetime, timedelta
#
# import backtrader as bt
#
# from app.core.backtrade.store import CCXTStore
# from app.core.backtrade.template import StoreStrategy
#
#
# def run():
#     global cerebro, config, store, broker
#     cerebro = bt.Cerebro(quicknotify=True)
#     # Add the strategy
#     cerebro.addstrategy(StoreStrategy)
#     # Create our store
#     config = {'apiKey': "KF1ELZxnpyCVjoV1TnagFqbr0dGaw2VvMwLylwVoUXU6bN7OPTASddFwyQWFNsnt",
#               'secret': "3f3Yaew7mWDJrZLcr5FQAYq4kdpqkgcsFL8MQQZRP6KB9SKOpexj1Ua7ahGKxSiJ",
#               'enableRateLimit': True,
#               }
#     # IMPORTANT NOTE - Kraken (and some other exchanges) will not return any values
#     # for get cash or value if You have never held any BNB coins in your account.
#     # So switch BNB to a coin you have funded previously if you get errors
#     store = CCXTStore(exchange='binance', currency='USDT', config=config, retries=5, debug=False)
#     # Get the broker and pass any kwargs if needed.
#     # ----------------------------------------------
#     # Broker mappings have been added since some exchanges expect different values
#     # to the defaults. Case in point, Kraken vs Bitmex. NOTE: Broker mappings are not
#     # required if the broker uses the same values as the defaults in CCXTBroker.
#     broker_mapping = {
#         'order_types': {
#             bt.Order.Market: 'market',
#             bt.Order.Limit: 'limit',
#             bt.Order.Stop: 'stop-loss',  # stop-loss for kraken, stop for bitmex
#             bt.Order.StopLimit: 'stop limit'
#         },
#         'mappings': {
#             'closed_order': {
#                 'key': 'status',
#                 'value': 'closed'
#             },
#             'canceled_order': {
#                 'key': 'result',
#                 'value': 1}
#         }
#     }
#     broker = store.getbroker(broker_mapping=broker_mapping)
#     cerebro.setbroker(broker)
#     # Get our data
#     # Drop newest will prevent us from loading partial data from incomplete candles
#     hist_start_date = datetime.utcnow() - timedelta(minutes=50)
#     klines = store.getdata(dataname='OPUSDT', name="OPUSDT",
#                            timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
#                            compression=1, ohlcv_limit=50, drop_newest=True)  # , historical=True)
#     # Add the feed
#     cerebro.adddata(klines)
#     # Run the strategy
#     cerebro.run()
#
#
# run()
