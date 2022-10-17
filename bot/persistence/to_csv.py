from .persistence import Persistence
from os.path import isfile
import pandas as pd


class CSV(Persistence):
    CSV_FOLDER = "../data"

    def __init__(self, pair: str, columns: list[str]) -> None:
        self.filename = f"{self.CSV_FOLDER}/{pair}.csv"
        self.columns = columns

    def write_sell(self, row: dict):
        table = pd.read_csv(self.filename)
        last_row = table.iloc[-1].to_dict()
        last_row.update(row)
        table = table.iloc[0:-1]
        table = pd.concat([table, pd.DataFrame([last_row])])
        table.to_csv(self.filename, index=False, header=True)

    def write_buy(self, row: dict):
        use_header = not isfile(self.filename)
        pd.DataFrame([row]).to_csv(self.filename, mode='w' if use_header else 'a', index=False, header=use_header)
