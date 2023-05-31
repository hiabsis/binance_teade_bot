import csv
import datetime as dt
import os

import pandas as pd
import tqdm
from loguru import logger

from app.core.cctx.adapter import CCtxAdapter as CctxClient
from app.core.config import Config
from app.core.utils.dateutil import DateUtil

interval_second = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "2h": 72000,
    "4h": 14400,
    "1d": 86400,
}
_ohlv_head = ["Time", "Open", "Close", "High", "Low", "Volume"]


class OhlvUtil:
    @staticmethod
    def load_ohlv_as_pd(symbol: str, timeframe: str, start: dt.datetime = None,
                        end: dt.datetime = None) -> pd.DataFrame:
        logger.debug("加载数据 {}_{}".format(symbol, timeframe))
        filepath = OhlvUtil.symbol_local_path(symbol, timeframe)
        if not os.access(filepath, os.X_OK):
            # 更新本地数据
            filepath = OhlvUtil.download_ohlv(symbol=symbol, timeframe=timeframe, )
        # 读取数据
        kines = pd.read_csv(filepath, parse_dates=True, skiprows=0, header=0)
        last_row = kines.tail(1)
        if end is None:
            end = dt.datetime.now()
        if start is None:
            return kines
        start_str = DateUtil.datetime_to_format(start)
        end_str = DateUtil.datetime_to_format(end)
        # 更新本地数据

        if end_str > last_row['Time'].iloc[0]:
            OhlvUtil.download_ohlv(symbol=symbol, timeframe=timeframe,
                                   since=DateUtil.datetime_to_timestamp(start) * 1000)
            kines = pd.read_csv(filepath, parse_dates=True, skiprows=0, header=0)

        # 筛选数据
        kines = kines[(kines['Time'] <= end_str) & (kines['Time'] >= start_str)]
        kines.set_index('Time')
        return kines

    @staticmethod
    def symbol_local_path(symbol: str, timeframe: str):
        resource = Config.resource_path()
        filepath = resource + '\\ohlv\\' + symbol.replace("/", '-')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath + "\\" + symbol.replace("/", '-') + '_' + timeframe + '.csv'

    @staticmethod
    def download_ohlv(symbol: str, timeframe: str, since: int = None, ):
        """
        下载数据

        :return:
        """
        filepath = OhlvUtil.symbol_local_path(symbol, timeframe)
        logger.info("下载数据 {}_{}".format(symbol, timeframe))

        if os.path.exists(filepath):
            # 读取最新时间
            with open(filepath, 'r') as file:
                reader = csv.reader(file)
                rows = list(reader)
                last_row = rows[-1]
                since = DateUtil.format_to_timestamp(last_row[0]) * 1000 + interval_second[timeframe] * 1000
                logger.info(
                    "下载数据 本地最新数据 {}".format(DateUtil.timestamp_to_format(since / 1000)))
        if since is None:
            since = CctxClient.query_begin_timestamp(symbol)
        limit = 300
        from datetime import datetime
        stop_tmp = datetime.now().timestamp() * 1000
        size = (stop_tmp - since) / 1000 / interval_second[timeframe] / limit + 1
        pbar = tqdm.trange(0, int(size), 1)
        data = []
        for idx, element in enumerate(pbar):
            fetch_ohlcv = CctxClient.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since, limit=limit)
            if fetch_ohlcv is None or len(fetch_ohlcv) == 0:
                break
            # 更新查询时间
            for index in range(len(fetch_ohlcv)):
                ohlv = fetch_ohlcv[index]
                datetime = DateUtil.timestamp_to_format(ohlv.timestamp / 1000)
                data.append(
                    [datetime, ohlv.openPrice, ohlv.closePrice, ohlv.highestPrice, ohlv.lowestPrice, ohlv.volume])

            since = fetch_ohlcv[len(fetch_ohlcv) - 1].timestamp + interval_second[timeframe] * 1000
            pbar.set_description(
                f"No.{idx}: [{symbol}-{timeframe}]")
            if len(data) > 0:
                OhlvUtil.__ohlv_to_csv(data, filepath, _ohlv_head)
                data.clear()
        logger.info("{}-{} 位置:{}".format(symbol, timeframe, filepath))

        return filepath

    @staticmethod
    def __ohlv_to_csv(data: [], save_path: str, head):
        """
        数据保存为csv

        """

        if not os.path.exists(save_path):
            with open(save_path, 'w') as csvfile:
                writer = csv.writer(csvfile, lineterminator='\n')
                writer.writerow(head)
        with open(save_path, 'a') as csvfile:
            writer = csv.writer(csvfile, lineterminator='\n')
            writer.writerows(data)
