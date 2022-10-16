from urllib.error import HTTPError
import requests
import os
from time import sleep
from requests import JSONDecodeError

class Trend:
    def __init__(self):
        self.KEY = os.getenv('RSI_API_KEY', '')
        if not self.KEY:
            raise EnvironmentError("Missing api key: RSI_API_KEY")
        self.session = requests.Session()

    def get_rsi(self, pair: str, interval: str='1h') -> float:
        """
            interval: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 12h, 1d, 1w
        """
        return round(self.request(f"https://api.taapi.io/rsi?secret={self.KEY}&exchange=binance&symbol={pair}&interval={interval}")['value'], 3)

    def request(self, url: str):
        attempts = 1
        while attempts < 5:
            try:
                response = self.session.get(url)
                response.raise_for_status()
                return response.json()
            except (ConnectionError, JSONDecodeError, HTTPError) as ex:
                print(ex)
                attempts += 1
                sleep(16)
        raise ValueError(f"Too many retries on {url}")

