import os
from collections import OrderedDict

import backtrader as bt
import quantstats
from backtrader import AutoOrderedDict
from loguru import logger

from app.core.config import Config


class StrategyAnalyzedResult:
    # 收益率：收益率是衡量策略表现的最基本指标之一，通常用总收益率、年化收益率、月度收益率和每日收益率等指标来衡量。
    roi: float
    #
    # 夏普比率：夏普比率是衡量策略表现的重要指标之一，衡量的是策略收益相对于风险的表现。夏普比率越高，则策略表现越好。
    sharpeRatio: float
    # 最大回撤：最大回撤是衡量策略表现的另一个重要指标，衡量的是策略最大损失能力。最大回撤越小，则策略表现越好。
    maxDrawDown: float
    # 胜率
    win_percentage: float
    # 盈亏比
    profit_ratio: float
    # 赢次数
    win_num: int = 1
    # 输次数
    lost_num: int = 1
    # 最大赢次数
    win_longest: int = 1
    # 最大输次数
    lost_longest: int = 1
    # 年化率
    annualized_rates: dict = {}


class BackTradeClient:
    @staticmethod
    def default_cerebro(cash=1000000.0, commission=0.001, enable_short=False) -> bt.Cerebro:
        """

        """
        # 加载backtrader引擎
        cerebro = bt.Cerebro()
        # 是否可以做空
        cerebro.broker.set_shortcash(enable_short)

        # 策略加进来
        cerebro.addsizer(bt.sizers.FixedSize, stake=1)
        # 设置以收盘价成交，作弊模式
        cerebro.broker.set_coc(False)
        cerebro.broker.set_cash(cash)
        # 设置手续费
        cerebro.broker.setcommission(commission=commission)

        return cerebro

    @staticmethod
    def console_analyze(cerebro: bt.Cerebro) -> StrategyAnalyzedResult:
        start_clash = cerebro.broker.getvalue()

        # 天机分析策略
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')
        cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
        strats = cerebro.run()
        logger.info("策略结果分析报告")
        symbols = set()
        for data in cerebro.datas:
            symbols.add(data._name)
        logger.info('交易品种: {}'.format(symbols))
        logger.info('启动资金: %.2f' % start_clash)
        # 输出最终价值
        logger.info('回测资金: %.2f' % cerebro.broker.getvalue())

        asr = StrategyAnalyzedResult()
        asr.profit_ratio = cerebro.broker.getvalue() / start_clash * 100
        for result in strats:
            # 夏普比率

            sharpe_analysis: OrderedDict = result.analyzers.sharpe.get_analysis()
            for _, ratio in sharpe_analysis.items():
                try:

                    logger.info('夏普比率: {} %', round(ratio * 100, 2))
                    asr.sharpeRatio = ratio * 100
                except  Exception as e:
                    logger.error("无法解析夏普比率")

            #
            pyfoliozer = result.analyzers.getbyname('pyfolio')
            returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
            # 记录交易次数和交易胜率
            try:

                trades_analysis: AutoOrderedDict = result.analyzers.trades.get_analysis()

                total_trades = trades_analysis.total.total
                total_wins = trades_analysis.won.total
                win_longest = trades_analysis.streak.won.longest
                lost_longest = trades_analysis.streak.lost.longest
                # for key, value in trades_analysis.items():
                #     value: AutoOrderedDict = value
                #     print(key, value)
                win_percentage = round(total_wins / total_trades * 100, 2)
                asr.win_num = total_wins
                asr.lost_num = total_trades - total_wins
                asr.win_longest = win_longest
                asr.lost_longest = lost_longest
                asr.win_percentage = win_percentage
                logger.info('交易次数: {}'.format(total_trades))
                logger.info('交易胜率: {}%'.format(win_percentage))
                logger.info('最大连胜次数: {}'.format(win_longest))
                logger.info('最大连输次数: {}'.format(lost_longest))
            except Exception as e:
                logger.info("无法获取交易信息")
            # 记录平均每个交易的收益率
            # average_trades_pnl = result.analyzers.pnl.get_analysis()['pnl']['average']
            # logger.info('平均每个交易的收益率: {}'.format(average_trades_pnl))
            # 回撤信息
            max_drawn_down = result.analyzers.DrawDown.get_analysis().max
            asr.maxDrawDown = max_drawn_down['drawdown']
            for key, value in max_drawn_down.items():
                logger.info('回撤 :  {} {}', key, round(value, 2))

            annual_return_analysis = result.analyzers.AnnualReturn.get_analysis()

            for key, value in annual_return_analysis.items():
                logger.info('{}: 年化率 {}%', key, round(value * 100, 2))
                asr.annualized_rates[key] = value * 100
        return asr

    @staticmethod
    def pyfolio_analyzer(cerebro: bt.Cerebro, is_show: bool = True, filename: str = "分析结果") -> str:
        """
        可视化分析 财务数据
        :return: 分享结果路径
        """
        resource = Config.resource_path()
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        back = cerebro.run()
        portfolio = back[0].analyzers.getbyname('pyfolio')
        returns, positions, transactions, gross_lev = portfolio.get_pf_items()
        returns.index = returns.index.tz_convert(None)
        output = resource + "\\analyzer\\pyfolio"

        if not os.path.exists(output):
            os.makedirs(output)
        output = "{}/{}.html".format(output, filename)

        quantstats.reports.html(returns, output=output, template_path=Config.strategy_report_template(),
                                download_filename=output,
                                title="")
        logger.info("文件位置{} ".format(output))
        return output
