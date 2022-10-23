from datetime import datetime
import time
from api.trend_api import Trend
from persistence.to_csv import CSV
from api.binance_api import Binance


class Trader:
    def __init__(self, pair: str, initial_usdt: float, initial_crypto: float, bin_key: str, bin_secret: str, simulator: bool=True) -> None:
        self._trends_api = Trend()
        self._binance_api = Binance(bin_key, bin_secret, pair, simulator)
        self._bought_price = None
        self.pair = pair.upper()
        self._persistence = CSV(pair.replace('/', ''), ['Amount', 'Buy price', 'Total buy', 'Sell price', 'Ratio', 'Gain/Loss', 'Total sell', 'Sell date'])
        self.usdt = initial_usdt
        self.crypto = initial_crypto
        self.simulator = simulator

    def _log_buy(self, amount: float, price: float) -> None:
        self._persistence.write_buy({
            'Amount': amount,
            'Buy price': f"{price}$",
            'Total buy': f"{round(amount * price, 2)}$",
        })

    def _buy(self):
        order = self._binance_api.buy_market_order(self.usdt)
        order = self._wait_until_complete(order['orderId'])
        self.crypto = order['executedQty']
        self._bought_price = order['price']
        self.usdt = 0
        self._log_buy(self.crypto, order['price'])
        print("buy")

    def _log_sell(self, price: float, ratio: float, gain_loss: float, total: float, date: datetime) -> None:
        self._persistence.write_sell({
            'Sell price': f"{price}$",
            'Ratio': f"{round(ratio, 2)}%",
            'Gain/Loss': f"{round(gain_loss, 2)}$",
            'Total sell': f"{round(total, 3)}$",
            'Sell date': date
        })

    def _sell(self):
        order = self._binance_api.sell_market_order(self.crypto)
        order = self._wait_until_complete(order['orderId'])
        self.crypto = 0
        self.usdt = order['executedQty'] * order['price']
        ratio = ((order['price'] - self._bought_price) / self._bought_price) * 100 if self._bought_price else 0.0
        gain = self.usdt - (self.crypto * (self._bought_price or 0))
        self._bought_price = None
        self._log_sell(order['price'], ratio, gain, self.usdt, datetime.now())
        print("sell")

    def start(self) -> None:
        while True:
            rsi = self._trends_api.get_rsi(self.pair, '1m')
            price = self._binance_api.buy_price if self.crypto else self._binance_api.sell_price
            ratio = ((price - self._bought_price) / self._bought_price) * 100 if self._bought_price else 0.0
            print(f"#### USDT: {self.usdt}$    #### Crypto: {self.crypto}    #### RSI:{format(rsi,'.2f')}    #### Ratio: {format(ratio,'.2f')}% ####")
            if not self.crypto and rsi <= 30:  # 30
                self._buy()
            elif self.crypto and rsi >= 70:  # 70
                self._sell()
                print(f"Ratio: {round(ratio, 4)}%")
            time.sleep(16)

    def _wait_until_complete(self, order_id: int):
        while not (filled_order := self._binance_api.has_completed(order_id)):
            time.sleep(1)
        return filled_order
