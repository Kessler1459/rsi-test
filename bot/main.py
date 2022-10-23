from dotenv import load_dotenv
from trading.trader import Trader
import os
import argparse

def run(pair, initial_usdt, initial_crypto, binance_key, binance_secret, testing):
    trader = Trader(pair, float(initial_usdt), float(initial_crypto), binance_key, binance_secret, testing)
    trader.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--operation', type=str, choices=['trading', 'testing'], default='testing', required=False)
    args = parser.parse_args()
    load_dotenv()
    testing = args.operation != 'trading'
    pair = os.getenv('PAIR', '')
    initial_usdt = os.getenv("INITIAL_USDT", '')
    initial_crypto = os.getenv("INITIAL_CRYPTO", '')
    binance_key = os.getenv('BINANCE_API_KEY', '')
    binance_secret = os.getenv("BINANCE_SECRET_KEY", '')
    binance_key_testing = os.getenv('BINANCE_API_KEY_TESTING', '')
    binance_secret_testing = os.getenv("BINANCE_SECRET_KEY_TESTING", '')
    enviromentals = [pair, initial_usdt, initial_crypto]
    if testing:
        enviromentals.extend([binance_key_testing, binance_secret_testing, testing])
    else:
        enviromentals.extend([binance_key, binance_secret, testing])
    if not all(enviromentals):
        raise EnvironmentError("Missing variables")
    run(*enviromentals)
