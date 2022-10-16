from abc import abstractclassmethod


class Persistence:

    @abstractclassmethod
    def __init__(self, pair: str, columns: list[str]) -> None:
        pass

    @abstractclassmethod
    def write_buy(self, row: dict):
        pass

    @abstractclassmethod
    def write_sell(self, row: dict):
        pass
