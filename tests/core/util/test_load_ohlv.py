import unittest

from app.core.utils.cctx import OhlvUtil


class Test(unittest.TestCase):
    def test_load_ohlv(self):
        OhlvUtil.load_ohlv_as_pd('ETH/USDT', timeframe='1d')
