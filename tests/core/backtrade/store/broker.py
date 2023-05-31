# import backtrader as bt
#
# from app.core.backtrade.store import CCXTStore
#
# config = {'apiKey': "KF1ELZxnpyCVjoV1TnagFqbr0dGaw2VvMwLylwVoUXU6bN7OPTASddFwyQWFNsnt",
#           'secret': "3f3Yaew7mWDJrZLcr5FQAYq4kdpqkgcsFL8MQQZRP6KB9SKOpexj1Ua7ahGKxSiJ",
#           'enableRateLimit': True,
#           }
#
# store = CCXTStore(exchange='binance', currency='ETH', config=config, retries=5, debug=False)
#
# # Get the broker and pass any kwargs if needed.
# # ----------------------------------------------
# # Broker mappings have been added since some exchanges expect different values
# # to the defaults. Case in point, Kraken vs Bitmex. NOTE: Broker mappings are not
# # required if the broker uses the same values as the defaults in CCXTBroker.
# broker_mapping = {
#     'order_types': {
#         bt.Order.Market: 'market',
#         bt.Order.Limit: 'limit',
#         bt.Order.Stop: 'stop-loss',  # stop-loss for kraken, stop for bitmex
#         bt.Order.StopLimit: 'stop limit'
#     },
#     'mappings': {
#         'closed_order': {
#             'key': 'status',
#             'value': 'closed'
#         },
#         'canceled_order': {
#             'key': 'result',
#             'value': 1}
#     }
# }
#
# broker = store.getbroker(broker_mapping=broker_mapping)
#
# size = broker.get_wallet_balance('ETH')
#
# print('ETH ', broker.get_wallet_balance('ETH'))
# print('USDT', broker.get_wallet_balance('USDT'))
# print('cash', broker.getcash())
# print('position', broker.positions)
