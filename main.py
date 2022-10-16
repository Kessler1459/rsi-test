from dotenv import load_dotenv
from trading.simulator import Simulator
import os

load_dotenv()

pair = os.getenv('PAIR')
initial_usdt = os.getenv("INITIAL_USDT")
initial_crypto= os.getenv("INITIAL_CRYPTO")
if not all([pair, initial_usdt, initial_crypto]):
    raise EnvironmentError("Missing variables")


trader = Simulator(pair, float(initial_usdt), float(initial_crypto))

trader.start()
