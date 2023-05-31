import re
from datetime import datetime

import backtrader


class BackTradeParamsUtil:
    @staticmethod
    def parse_timeframe(timeframe) -> (int, backtrader.TimeFrame):
        math = re.search(r'\d+', timeframe)
        if math:
            compression = int(math.group())
        else:
            raise ValueError(" {} timeframe not support".format(timeframe))
        if timeframe.endswith('d'):
            timeframe = backtrader.TimeFrame.Days
        elif timeframe.endswith('h'):
            timeframe = backtrader.TimeFrame.Minutes
            compression = compression * 60
        elif timeframe.endswith('m'):
            timeframe = backtrader.TimeFrame.Minutes
        return compression, timeframe


class CoreRunParams:
    symbol: str
    timeframe: str
    start: datetime = None
    end: datetime = None
    run_mode = 'test'

    def __init__(self, params: dict = None):
        if params is None:
            return
        if 'symbol' in params:
            self.symbol = params['symbol']
        if 'timeframe' in params:
            self.timeframe = params['timeframe']
        if 'start' in params:
            self.start = params['start']
        if 'end' in params:
            self.end = params['end']
        if 'run_mode' in params:
            self.run_mode = params['run_mode']