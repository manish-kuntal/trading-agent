# AI Intraday Trading Agent

Autonomous NSE/BSE intraday trading system with paper trading, risk controls, and mobile dashboard.

## Quick Start (Windows)

```bash
# 1. Setup
scripts\setup.bat

# 2. Fill .env with Angel One credentials

# 3. Test connection
scripts\run_test.bat

# 4. Run agent (paper mode by default)
scripts\run_agent.bat

# 5. Start API server (separate terminal)
scripts\run_api.bat
```

## Project Structure
```
trading-agent/
├── agent/          # Core trading logic
│   ├── data/       # Market data + feature engineering
│   ├── strategy/   # Signals + risk management
│   ├── execution/  # Virtual + live broker
│   └── db/         # Database models
├── api/            # FastAPI server (monitoring)
├── ml/             # Model training + backtesting
├── frontend/       # Mobile dashboard (Phase 6)
├── infra/          # VPS deployment (Phase 5)
└── scripts/        # Windows setup scripts
```

## Phases
- **Phase 1-3**: Paper trading (PAPER_TRADING=true in .env)
- **Phase 4**: Set PAPER_TRADING=false + Angel API live
- **Phase 5**: Docker deploy to VPS
- **Phase 6**: Mobile dashboard via `frontend/`

## Risk Defaults (.env)
| Parameter | Default | Meaning |
|-----------|---------|---------|
| DAILY_LOSS_LIMIT_PCT | 0.02 | 2% capital max loss/day |
| MAX_POSITION_PCT | 0.05 | 5% capital per trade |
| STOP_LOSS_PCT | 0.015 | 1.5% SL from entry |
| MAX_OPEN_POSITIONS | 3 | Max concurrent trades |
