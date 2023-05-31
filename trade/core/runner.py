from typing import List

import pandas as pd
from loguru import logger

from app.core.utils.cctx import OhlvUtil
from trade.core.command.keyboard import ContinueCommand
from trade.core.command.order import ClosePositionCommand
from trade.core.config import RunParamsFactory, RunParams
from trade.model.account import AccountFactory, Account
from trade.model.enums import RunnerStatus, OrderStatus
from trade.utils.colour import ColourTxtUtil


def operation_help() -> str:
    return "{} {}: Busy {}: Sell {}: Close {}:Account {}: Next".format(
        ColourTxtUtil.cyan('Operation'),
        ColourTxtUtil.red("B"),
        ColourTxtUtil.red("S"),
        ColourTxtUtil.red("C"),
        ColourTxtUtil.red("A"),
        ColourTxtUtil.red("Enter"),

    )


def klines_format_str(row, symbol, timeframe):
    return "\n{} {} {} \n{}: {} {}: {} {}: {} {}: {} {}: {} {}:{}\n".format(
        ColourTxtUtil.cyan("行情"),

        symbol,
        timeframe,

        ColourTxtUtil.blue("Time"),
        row['Time'],
        ColourTxtUtil.blue("Open"),
        row['Open'],
        ColourTxtUtil.blue("High"),
        row['High'],
        ColourTxtUtil.blue("Low"),
        row['Low'],
        ColourTxtUtil.blue(
            "Close"),
        row['Close'],
        ColourTxtUtil.blue(
            "Volume"),
        row['Volume'])


class Runner:
    account: Account
    logger = logger
    params: RunParams
    klines: dict = {}
    command: List = []
    status: RunnerStatus = RunnerStatus.Stop

    def __init__(self):
        self.log("初始化")
        self.account = AccountFactory.load_by_config()
        self.params = RunParamsFactory.load_by_config()
        for symbol in self.params.symbols:
            self.klines[symbol] = OhlvUtil.load_ohlv_as_pd(symbol=symbol,
                                                           timeframe=self.params.timeframe,
                                                           start=self.params.from_time,
                                                           end=self.params.to_time)
        self.load_command()

    def log(self, txt):
        print(txt)
        # self.logger.debug(txt)

    def load_command(self):
        self.command.append(ContinueCommand())

    def handle_command(self, command):
        for co in self.command:
            if co.execute(self, command):
                break

    def run(self):
        # 打印账户信息
        self.log(self.account.format_str())
        for symbol, kline in self.klines.items():
            self.handle_order(symbol, kline)
            self.trade(symbol, self.params.timeframe, kline)

    def trade(self, symbol: str, timeframe: str, klines: pd.DataFrame):

        for index, row in klines.iterrows():
            # 打印行情数据
            self.log(klines_format_str(row, symbol, timeframe))
            while True:
                # 操作指南
                self.log(operation_help())
                command = input("{}： ".format(ColourTxtUtil.blue('指令')))
                command = command.replace(' ', '')
                self.handle_command(command)
                if self.status == RunnerStatus.Next:
                    self.status = RunnerStatus.Stop
                    break

    def handle_order(self, symbol, kline):
        account = self.account
        # 处理平仓命令：
        if symbol in account.close_position_orders:
            orders = account.close_position_orders[symbol]
            if orders is None:
                account.create_order[symbol] = []
                orders = []

            for order in orders[:]:
                ClosePositionCommand().execute(account, order, kline)
                if order.status == OrderStatus.Cancel or order.status == OrderStatus.Complete:
                    orders.remove(order)

        if symbol in account.create_order:
            orders = account.create_order[symbol]
            if orders is None:
                account.create_order[symbol] = []
                orders = []

            for order in orders[:]:
                ClosePositionCommand().execute(account, order, kline)
                if order.status == OrderStatus.Cancel or order.status == OrderStatus.Complete:
                    orders.remove(order)


class RunnerFactory:

    @staticmethod
    def default_runner() -> Runner:
        return Runner()
