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
            'Amount': str(amount),
            'Buy price': f"{price}$",
            'Total buy': f"{round(amount * price, 2)}$",
        })

    def _buy(self):
        order = self._binance_api.buy_market_order(self.usdt)
        order = self._wait_until_complete(order['orderId'])
        self.crypto = float(order['executedQty'])
        self._bought_price = float(order['cummulativeQuoteQty']) / self.crypto
        self.usdt = self.usdt - float(order['cummulativeQuoteQty'])
        self._log_buy(self.crypto, self._bought_price)
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
        sold_crypto = float(order['executedQty'])
        new_usdt = float(order['cummulativeQuoteQty'])
        self.crypto -= sold_crypto
        self.usdt += new_usdt
        sell_price = new_usdt / sold_crypto
        ratio = ((sell_price - self._bought_price) / self._bought_price) * 100 if self._bought_price else 0.0
        gain = new_usdt - (sold_crypto * (self._bought_price or 0))
        self._bought_price = None
        self._log_sell(sell_price, ratio, gain, self.usdt, datetime.now())
        print("sell")
        print(f"Ratio: {round(ratio, 4)}%")

    def start(self) -> None:
        while True:
            rsi = self._trends_api.get_rsi(self.pair, '1m')
            price = self._binance_api.buy_price if self.crypto else self._binance_api.sell_price
            ratio = ((price - self._bought_price) / self._bought_price) * 100 if self._bought_price else 0.0
            print(f"#### USDT: {format(self.usdt,'.2f')}$    #### Crypto: {self.crypto}    #### RSI:{format(rsi,'.2f')}    #### Ratio: {format(ratio,'.2f')}% ####")
            if not self._bought_price and rsi <= 30:  # 30
                self._buy()
            elif self._bought_price and rsi >= 70:  # 70
                self._sell()
            time.sleep(16)

    def _wait_until_complete(self, order_id: int):
        has_completed = False
        order = {}
        while not has_completed:
            order = self._binance_api.query_order(order_id)
            has_completed = order['status'] == 'FILLED'
            if not has_completed:
                time.sleep(1)
        return order
