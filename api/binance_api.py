from binance.spot import Spot

class Binance:
    client: Spot

    def __init__(self) -> None:
        self.client = Spot()

    def get_book(self, symbol: str):
        return self.client.book_ticker(symbol)

    def get_sell_price(self, symbol: str):
        return self.client.book_ticker(symbol).get('askPrice')

    def get_buy_price(self, symbol: str):
        return self.client.book_ticker(symbol).get('bidPrice')
