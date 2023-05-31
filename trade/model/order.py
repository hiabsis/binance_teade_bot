from trade.model.enums import SideType, OrderStatus
from trade.utils.colour import ColourTxtUtil

ORDER_UUID = 1


def generate_order_uuid():
    global ORDER_UUID
    ORDER_UUID += 1
    return ORDER_UUID


class Order:
    uuid: int
    symbol: str
    price: float
    size: float
    side: SideType
    status: OrderStatus

    def __init__(self, price: float, size: float, side: SideType, symbol: str = None,
                 status: OrderStatus = OrderStatus.Execute):
        self.ID = generate_order_uuid()
        self.symbol = symbol
        self.price = price
        self.size = size
        self.side = side

    def format_str(self) -> str:
        return "\n{}:{} {}: {} {}: {}  {}: {} {}: {}\n".format(

            ColourTxtUtil.orange('Symbol'),
            self.symbol,
            ColourTxtUtil.orange('Side'),
            self.side.name,
            ColourTxtUtil.orange('Id'),
            self.ID,
            ColourTxtUtil.orange('Price'),
            self.price,
            ColourTxtUtil.orange('Size'),
            self.size
        )

    def is_buy(self) -> bool:
        return self.side.is_buy()

    def is_sell(self) -> bool:
        return self.side.is_sell()


class OrderFactory:
    @staticmethod
    def create_buy_order(price: float, size: float, symbol: str) -> Order:
        return Order(price=price, size=size, side=SideType.Buy, symbol=symbol)

    @staticmethod
    def create_sell_order(price: float, size: float, symbol: str) -> Order:
        return Order(price=price, size=size, side=SideType.Sell, symbol=symbol)
