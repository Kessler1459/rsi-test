import time
from binance.websocket.spot.websocket_client import SpotWebsocketClient
from binance.spot import Spot

class Binance:
    sell_price: float
    buy_price: float
    def __init__(self, api_key: str, api_secret: str, symbol: str, testing: bool=True) -> None:
        self.symbol = symbol.replace('/', '')
        self.testing = testing
        endpoint = 'https://testnet.binance.vision' if testing  else "https://api.binance.com"
        self.spot = Spot(api_key, api_secret, base_url=endpoint, show_limit_usage=True)
        self.ws_client = SpotWebsocketClient("wss://testnet.binance.vision")
        self.ws_client.start()
        self.__book_subscribe()


    def __book_subscribe(self):
        def set_prices(book: dict):
            self.sell_price = float(book.get('a', 0))
            self.buy_price = float(book.get('b', 0))
        self.ws_client.book_ticker(1, set_prices, self.symbol)
        time.sleep(10)


    def set_buy_limit_order(self, quantity: float, price: float):
        return self.__set_limit_order('BUY', quantity, price)


    def set_sell_limit_order(self, quantity: float, price: float):
        return self.__set_limit_order('SELL', quantity, price)


    def buy_market_order(self, usdt: float):
        return self.__set_market_order('BUY', usdt=usdt)


    def sell_market_order(self, crypto: float):
        return self.__set_market_order('SELL', crypto=crypto)


    def set_stop_loss_order(self, quantity: float, stop_price: float):
        self.spot.new_order_test(self.symbol, 'SELL', 'STOP_LOSS', quantity=quantity, stopPrice=stop_price)


    def query_order(self, order_id: int):
        """
        Weight: 2
        """
        return self.spot.get_order(self.symbol, orderId=order_id)['data']


    def __set_market_order(self, side: str, usdt: float|None = None, crypto: float|None = None):
        if usdt:
            params = {'quoteOrderQty': round(usdt, 4)}
        else:
            params = {"quantity": crypto}
        return self.spot.new_order(self.symbol, side, 'MARKET', **params)['data']


    def __set_limit_order(self, side: str, quantity: float, price: float):
        return self.spot.new_order(self.symbol, side, 'LIMIT', timeInForce='GTC', quantity=quantity, price=price)['data']


    def __del__(self):
        print("Closing connection")
        self.ws_client.stop()
