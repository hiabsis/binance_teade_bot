from trade.model.enums import SideType
from trade.model.order import Order

POSITION_UUID = 1


def generate_order_uuid():
    global POSITION_UUID
    POSITION_UUID += 1
    return POSITION_UUID


class Position(Order):
    uuid: int
    symbol: str
    price: float
    size: float
    side: SideType


class PositionFactory:
    @staticmethod
    def create_buy_position(price: float, size: float, symbol: str) -> Order:
        return Position(price=price, size=size, side=SideType.Buy, symbol=symbol)

    @staticmethod
    def create_sell_position(price: float, size: float, symbol: str) -> Order:
        return Position(price=price, size=size, side=SideType.Sell, symbol=symbol)



