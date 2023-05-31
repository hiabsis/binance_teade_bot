# core/config.py
from configparser import ConfigParser

from main import fetch_app_path

config_filename = './config.ini'
config = ConfigParser()
# 项目根路径


config.read(config_filename, encoding='utf-8')

APP_PATH = fetch_app_path()

# 静态资源位置
RESOURCE_PATH = APP_PATH + '/static'
# 交易所的密钥
CCXT_API_KEY = config.get('ccxt', 'api_key')
if CCXT_API_KEY == 'None':
    CCXT_API_KEY = None
CCXT_SECRET = config.get('ccxt', 'secret')
if CCXT_SECRET == 'None':
    CCXT_SECRET = None
# 策略配置
STRATEGY_RUN_MOD = config.get('strategy', 'run_mod')

BALANCE = float(config.get('trade', 'balance'))
FEE = float(config.get('trade', 'fee'))
SYMBOLS = config.get('trade', 'symbols').split(',')
TIMEFRAME = config.get('trade', 'timeframe')
FROM_TIME = config.get('trade', 'from_time')
TO_TIME = config.get('trade', 'to_time')
ENABLE_SHORT = config.get('trade', 'enable_shore')


class Config:

    @staticmethod
    def resource_path() -> str:
        return RESOURCE_PATH

    @staticmethod
    def ccxt_api_key() -> str:
        return CCXT_API_KEY

    @staticmethod
    def cctx_secret() -> str:
        return CCXT_SECRET

    @staticmethod
    def strategy_report_template() -> str:
        return r'{}\hepler\report.html'.format(APP_PATH)

    @staticmethod
    def strategy_run_mod():
        return STRATEGY_RUN_MOD
