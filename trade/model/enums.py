from enum import Enum


class SideType(Enum):
    Buy = 1
    Sell = -1

    @property
    def name(self):

        if self.value == -1:
            return "Sell"
        elif self.value == 1:
            return "Buy"

    def is_buy(self) -> bool:
        return self.value == 1

    def is_sell(self) -> bool:
        return self.value == -1


class RunnerStatus(Enum):
    Stop = 1
    Next = 2


class OrderStatus(Enum):
    # 执行中
    Execute = 'Execute'
    # 取消
    Cancel = 'Cancel'
    # 完成
    Complete = 'Complete'

    @property
    def name(self):
        return self.value
