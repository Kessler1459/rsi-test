from datetime import datetime
from .trader import Trader


class Simulator(Trader):
    def _buy(self, price: float) -> bool:
        self.crypto = self.usdt / price
        self._bought_price = price
        self.usdt = 0
        print("buy")
        self._log_buy(self.crypto, price)
        return True

    def _sell(self, price: float, ratio: float) -> bool:
        self.usdt = self.crypto * price
        self._log_sell(price, ratio, self.usdt - (self.crypto * (self._bought_price or 0)), self.usdt, datetime.now())
        self.crypto = 0
        self._bought_price = None
        print('sell')
        return True