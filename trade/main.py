import pandas as pd

from app.core.utils.cctx import OhlvUtil
from trade.config import Account, RunParams, Order, Position
from trade.utils.colour import ColourTxtUtil

CommandQueue = []

StopSign = False


def send_command(command):
    CommandQueue.append(command)


def on_press(key):
    print('Key {} '.format(key))
    if key == "Key.space":
        key = 'space'

    send_command(key)


def fetch_close_ratio() -> float:
    close_ratio = 0

    while True:
        try:
            close_ratio = input("{}： ".format(ColourTxtUtil.blue('平仓比例')))
            close_ratio = float(close_ratio)
            if 0 < close_ratio <= 100:
                break
        except ValueError:
            print("{}".format(ColourTxtUtil.red('输入不合法，请重新输入')))
            continue

    return close_ratio


def fetch_order_params():
    side, price, size = 0, 0, 0
    while True:
        try:
            side = input("{}： ".format(ColourTxtUtil.blue('方向(做多:1 做空:-1)')))
            side = int(side)
            if side == 1 or side == -1:
                break
            else:
                print("{}".format(ColourTxtUtil.red('输入不合法，请重新输入')))
        except ValueError:
            print("{}".format(ColourTxtUtil.red('输入不合法，请重新输入')))
            continue

    while True:
        try:
            price = input("{}： ".format(ColourTxtUtil.blue('价格')))
            price = float(price)
        except ValueError:
            print("{}".format(ColourTxtUtil.red('输入不合法，请重新输入')))
            continue
        else:
            break
    while True:
        try:
            size = input("{}： ".format(ColourTxtUtil.blue('数量')))
            size = float(size)
        except ValueError:
            print("{}".format(ColourTxtUtil.red('输入不合法，请重新输入')))
            continue
        else:
            break
    return side, price, size


def operation_help() -> str:
    return "{} {}: Busy {}: Sell {}: Close {}:Account {}: Next".format(
        ColourTxtUtil.cyan('Operation'),
        ColourTxtUtil.red("B"),
        ColourTxtUtil.red("S"),
        ColourTxtUtil.red("C"),
        ColourTxtUtil.red("A"),
        ColourTxtUtil.red("Enter"),

    )


class Main:
    name = "{}".format(ColourTxtUtil.red("交易模拟器"))
    account = Account()
    kines: pd.DataFrame

    sleep_time = 8
    temp_time = 8
    status = 'Normal'
    order_count = 0

    def __init__(self):
        self.params = RunParams()

    def generator_order_id(self) -> str:
        self.order_count += 1
        return str(self.order_count)

    def load_data(self):
        params = self.params
        self.kines = OhlvUtil.load_ohlv_as_pd(symbol=params.symbol,
                                              timeframe=params.timeframe,
                                              start=params.from_time,
                                              end=params.to_time)
        pass

    def run(self):
        self.load_data()

        for index, row in self.kines.iterrows():
            o = float(row['Open'])
            h = float(row['High'])
            l = float(row['Low'])
            c = float(row['Close'])
            self.handle_order(o, l, h)
            txt = self.name
            txt += "\n{} {} {} \n{}: {} {}: {} {}: {} {}: {} {}: {} {}:{}\n".format(
                ColourTxtUtil.cyan("行情"),

                self.params.symbol,
                self.params.timeframe,

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

            txt += self.account.detail()
            print(txt)
            while True:
                print(operation_help())
                command = input("{}： ".format(ColourTxtUtil.blue('输入指令')))
                command = command.replace(' ', '')
                if command.lower() == 'n' or command == '':
                    break
                elif command.lower() == 'b':
                    self.buy_command_handle(symbol=self.params.symbol)
                elif command.lower() == 's':
                    self.sell_command_handle(self.params.symbol)

            print("\n")

    def buy_command_handle(self, symbol) -> bool:
        side, price, size = fetch_order_params()

        if self.account.balance < price * size:
            print("{}".format(ColourTxtUtil.red("余额不足")))
            return False

        order = Order(ID=self.generator_order_id(), symbol=symbol, price=price, size=size, side=side)
        self.account.append_order(order)

        print("下单: ", order.detail())
        return True

    def sell_command_handle(self, symbol: str) -> bool:
        if self.account.position is None:
            print('{} '.format(ColourTxtUtil.red('仓位为空')))
            return False

        close_ratio = fetch_close_ratio()

        size = close_ratio * self.account.position.size

        order = Order(ID=self.generator_order_id(), symbol=symbol, price=0, size=size, side=0)
        self.account.append_order(order)
        print("平仓: ", order.detail())

    def handle_order(self, o: float, low: float, high: float):
        for order in self.account.orders[:]:
            if order.side == 0:
                size = self.account.position.size - order.size
                price = (o + high) / 2
                self.account.balance = size * price
                self.account.position.size -= size
                self.account.orders.remove(order)
        for order in self.account.orders[:]:

            if order.side == -1:
                if low < order.price:
                    self.account.balance -= order.size * order.price
                    self.account.orders.remove(order)
                    if self.account.position is None:
                        position = Position()
            elif order.size == 1:
                if high > order.price:
                    self.account.balance -= order.size * order.price
                    self.account.orders.remove(order)

    def handle_order(self):
        pass

    def close_command_handle(self):
        pass

    def stop(self):
        self.status = 'Stop'
        while self.status == 'Stop':
            message = input("请输入一个字符串：")
            print("您输入的字符串是：", message)

    def recover(self):
        self.sleep_time = self.sleep_time


app = Main()
# monitor_keyword_task = threading.Thread(target=app.monitor_keyword, args=())
# monitor_keyword_task.start()
# handler_command_task = threading.Thread(target=app.handler_command, args=())
# handler_command_task.start()

app.run()
