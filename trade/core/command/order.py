from loguru import logger

from trade.model.account import Account
from trade.model.enums import OrderStatus
from trade.model.order import Order
from trade.model.position import PositionFactory


class OrderCommand:
    logger = logger

    def log(self, txt):
        # self.logger.debug(txt)
        print(txt)

    def execute(self, account: Account, order, kline):
        raise NotImplementedError


def update_position_size(account, order, position):
    position.size = position.size - order.size
    if position.size == 0:
        position = None

    account.buy_positions[order.symbol] = position


class ClosePositionCommand(OrderCommand):

    def execute(self, account: Account, order, kline):
        # 检查是否有仓位
        if order.is_buy() and order.symbol in account.buy_positions:
            position = account.buy_positions[order.symbol]
            npl = (order.price - position.price) * order.size * (1 - account.fee)
            # 更新余额
            account.balance += npl
            # 更新仓位
            update_position_size(account, order, position)

            order.status = OrderStatus.Execute
            self.log('做多平仓')
            self.log("Symbol：{} 买入价{} 平仓价格{} 利润 {}".format(order.symbol, position.price, order.price, npl))

        else:
            self.log("平仓失败,由于未持仓")
            order.status = OrderStatus.Cancel
        if order.is_sell() and order.symbol in account.sell_positions:

            position = account.sell_positions[order.symbol]
            npl = (position.price - order.price) * order.size * (1 - account.fee)
            # 更新余额
            account.balance += npl
            # 更新仓位
            update_position_size(account, order, position)
            order.status = OrderStatus.Execute
            self.log('做空平仓')
            self.log("Symbol：{} 买入价{} 平仓价格{} 利润 {}".format(order.symbol, position.price, order.price, npl))
            pass
        else:
            order.status = OrderStatus.Cancel
            self.log("平仓失败,由于未持仓")


class BuyOderCommand(OrderCommand):

    def execute(self, account: Account, order, kline):
        # 检查余额
        cost = order.size * order.price

        if account.balance < cost:
            self.log("余额不足取消订单 订单ID：".format(order.ID))
            Order.status = OrderStatus.Cancel
        if order.is_buy():
            if order.price > (kline['Open'] + kline['High']) / 2:
                order.status = OrderStatus.Complete
                account.balance -= cost
                position = account.buy_positions[order.symbol]
                if position is None:
                    position = PositionFactory.create_buy_position(order.price, order.size, symbol=order.symbol)
                else:
                    position.size += order.size
                    position.price = (order.price * order.size + position.size + position.price) / (
                            order.size + position.size)

                account.buy_positions[order.symbol] = position
                self.log("订单成交 {}".format(order.format_str()))

        elif order.is_sell():
            if order.price > (kline['Open'] + kline['Low']) / 2:
                account.balance -= cost
                order.status = OrderStatus.Complete
                position = account.sell_positions[order.symbol]
                if position is None:
                    position = PositionFactory.create_sell_position(order.price, order.size, symbol=order.symbol)
                else:
                    position.size += order.size
                    position.price = (order.price * order.size + position.size + position.price) / (
                            order.size + position.size)
                account.sell_positions[order.symbol] = position
                self.log("订单成交 {}".format(order.format_str()))

    pass
