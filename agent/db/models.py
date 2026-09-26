from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Trade(Base):
    __tablename__ = "trades"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    symbol        = Column(String(20), nullable=False, index=True)
    token         = Column(String(10), default="")
    action        = Column(String(4))
    qty           = Column(Integer)
    entry_price   = Column(Float)
    exit_price    = Column(Float, nullable=True)
    sl_price      = Column(Float, nullable=True)
    pnl           = Column(Float, nullable=True)
    signal_conf   = Column(Float, default=0.0)
    signal_reason = Column(Text,  default="")
    order_id      = Column(String(50), default="")
    is_paper      = Column(Boolean, default=True)
    entry_time    = Column(DateTime, default=datetime.now, index=True)
    exit_time     = Column(DateTime, nullable=True)


class OpenPosition(Base):
    __tablename__ = "open_positions"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    symbol      = Column(String(20), nullable=False, unique=True)
    token       = Column(String(10), default="")
    qty         = Column(Integer)
    entry_price = Column(Float)
    sl_trigger  = Column(Float, nullable=True)
    is_paper    = Column(Boolean, default=True)
    entry_time  = Column(DateTime, default=datetime.now)
    updated_at  = Column(DateTime, default=datetime.now)


class DailyPnL(Base):
    __tablename__ = "daily_pnl"
    id           = Column(Integer, primary_key=True)
    date         = Column(String(10), unique=True, index=True)
    realized_pnl = Column(Float, default=0.0)
    trades_count = Column(Integer, default=0)
    win_count    = Column(Integer, default=0)
    capital_eod  = Column(Float, default=0.0)
    is_paper     = Column(Boolean, default=True)


class AgentLog(Base):
    __tablename__ = "agent_logs"
    id        = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    symbol    = Column(String(20), nullable=True)
    event     = Column(String(30))
    details   = Column(Text, default="")
    is_paper  = Column(Boolean, default=True)
