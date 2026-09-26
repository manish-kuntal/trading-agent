from abc import ABC, abstractmethod


class BaseBroker(ABC):
    """
    Abstract broker interface.
    Strategy code depends ONLY on this — swap virtual ↔ live
    by changing one line in agent/main.py.
    """

    @abstractmethod
    def login(self) -> bool: ...

    @abstractmethod
    def get_ltp(self, exchange: str, symbol: str, token: str) -> float: ...

    @abstractmethod
    def get_candles(self, token: str, interval: str,
                    from_date: str, to_date: str) -> list: ...

    @abstractmethod
    def place_order(self, symbol: str, token: str,
                    action: str, qty: int) -> str: ...

    @abstractmethod
    def place_stoploss(self, symbol: str, token: str, action: str,
                       qty: int, trigger: float, price: float) -> str: ...

    @abstractmethod
    def get_positions(self) -> list: ...

    @abstractmethod
    def close_all_positions(self): ...
