"""Basic broker interface tests."""
import pytest
from unittest.mock import MagicMock, patch
from agent.execution.virtual_broker import VirtualBroker


@pytest.fixture
def vbroker():
    b = VirtualBroker(capital=100_000)
    # Mock the underlying Angel broker
    b._angel = MagicMock()
    b._angel.login.return_value = True
    b._angel.get_ltp.return_value = 2500.0
    b._angel.get_candles.return_value = []
    b.login()
    return b


def test_buy_reduces_capital(vbroker):
    vbroker.place_order("RELIANCE-EQ", "2885", "BUY", 10)
    assert vbroker.capital < 100_000

def test_sell_increases_capital(vbroker):
    vbroker.place_order("RELIANCE-EQ", "2885", "BUY",  10)
    cap_after_buy = vbroker.capital
    vbroker.place_order("RELIANCE-EQ", "2885", "SELL", 10)
    assert vbroker.capital > cap_after_buy

def test_pnl_zero_on_same_price(vbroker):
    vbroker.place_order("RELIANCE-EQ", "2885", "BUY",  10)
    vbroker.place_order("RELIANCE-EQ", "2885", "SELL", 10)
    assert abs(vbroker.daily_pnl) < 0.01

def test_insufficient_capital_blocked(vbroker):
    vbroker.capital = 100
    order_id = vbroker.place_order("RELIANCE-EQ", "2885", "BUY", 10)
    assert order_id == ""
    assert vbroker.capital == 100
