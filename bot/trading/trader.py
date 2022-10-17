from datetime import datetime
from abc import abstractmethod
import time
from api.trend_api import Trend
from persistence.to_csv import CSV
from api.binance_api import Binance


class Trader:
    def __init__(self, pair: str, initial_usdt: float, initial_crypto: float, simulator: bool = True) -> None:
        self._trends_api = Trend()
        self._binance_api = Binance()
        self._bought_price = None
        self.pair = pair.upper()
        self._persistence = CSV(pair.replace('/', ''), ['Amount', 'Buy price', 'Total buy', 'Sell price', 'Ratio', 'Gain/Loss', 'Total sell', 'Sell date'])
        self.usdt = initial_usdt
        self.crypto = initial_crypto
        self.simulator = simulator

    def _log_buy(self, amount: float, price: float) -> None:
        self._persistence.append_to_csv({
            'Amount': amount,
            'Buy price': f"{price}$",
            'Total buy': f"{amount * price}$",
        })

    @abstractmethod
    def _buy(self, price: float) -> bool:
        pass

    def _log_sell(self, price: float, ratio: float, gain_loss: float, total: float, date: datetime) -> None:
        self._persistence.edit_last_row({
            'Sell price': f"{price}$",
            'Ratio': f"{ratio}%",
            'Gain/Loss': f"{gain_loss}$",
            'Total sell': f"{total}$",
            'Sell date': date
        })

    @abstractmethod
    def _sell(self, price: float, ratio: float) -> bool:
        pass

    def start(self) -> None:
        while True:
            rsi = self._trends_api.get_rsi(self.pair, '1m')
            book = self._binance_api.get_book(self.pair.replace('/', ''))
            buy_price = float(book['bidPrice'])
            sell_price = float(book['askPrice'])
            ratio = ((buy_price - self._bought_price) /
                     self._bought_price) * 100 if self._bought_price else 0.0
            print(f"#### USDT: {self.usdt}$    #### Crypto: {self.crypto}    #### RSI:{format(rsi,'.2f')}    #### Ratio: {format(ratio,'.2f')}% ####")
            if not self.crypto and rsi <= 30:  # 30
                self._buy(sell_price)
            elif self.crypto and rsi >= 70:  # 70
                self._sell(buy_price, ratio)
                print(f"Ratio: {round(ratio, 4)}%")
            time.sleep(16)
