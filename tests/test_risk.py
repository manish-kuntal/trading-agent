"""Risk manager tests."""
import pytest
from unittest.mock import MagicMock
from agent.strategy.risk import RiskManager


@pytest.fixture
def risk():
    broker = MagicMock()
    broker.daily_pnl = 0.0
    broker.initial_capital = 100_000.0
    broker.capital = 100_000.0
    broker.get_positions.return_value = []
    return RiskManager(broker)


def test_no_loss_no_breach(risk):
    risk.broker.daily_pnl = -500.0   # ₹500 loss < 2% of ₹1L
    assert not risk.daily_loss_exceeded()

def test_loss_cap_triggers(risk):
    risk.broker.daily_pnl = -2500.0  # ₹2500 >= 2% of ₹1L
    assert risk.daily_loss_exceeded()

def test_position_size_positive(risk):
    qty = risk.position_size(ltp=1500.0)
    assert qty >= 1

def test_stoploss_below_entry_for_buy(risk):
    trigger, limit = risk.calc_stoploss(entry_price=1000.0, action="BUY")
    assert trigger < 1000.0
    assert limit   < trigger
