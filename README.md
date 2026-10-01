<div align="center">

# ⚡ AI Intraday Trading Agent

### Autonomous NSE/BSE Intraday Trading System

**Paper Trading • Risk Management • Angel One SmartAPI • FastAPI • ML • Telegram • Ollama**

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Trading-Paper%20Mode-2EA44F?style=for-the-badge" alt="Paper Trading">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Ollama-Optional-black?style=for-the-badge" alt="Ollama">
</p>

<p>
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-running-the-system">Run</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-security">Security</a>
</p>

</div>

---

> [!IMPORTANT]
> **Paper trading is enabled by default.**
>
> This project is intended for educational and research purposes. Do **not** use real money until the complete system, broker integration, order handling, risk controls, and failure scenarios have been independently tested and reviewed.

---

## 🎯 What Is This?

**AI Intraday Trading Agent** is a Python-based trading system designed for NSE/BSE intraday workflows.

The project combines:

- 📊 Market-data processing
- 🧠 Strategy and signal generation
- 🛡️ Risk management
- 💰 Paper trading with virtual capital
- 🔌 Angel One SmartAPI integration
- 🤖 Optional local LLM support through Ollama
- 🌐 FastAPI monitoring API
- 📱 Telegram notifications
- 🧪 ML and backtesting components
- 🗄️ SQLite / PostgreSQL support
- ⚡ Redis support
- 🐳 Docker Compose support
- 📝 Application logging

---

# ✨ Features

| Feature | Description |
|---|---|
| 💰 **Paper Trading** | Trade using virtual capital while developing/testing |
| 🔌 **Angel One** | Broker integration through SmartAPI |
| 📊 **Market Data** | Market-data processing and technical indicators |
| 🧠 **Strategy Engine** | Signal generation and scheduled strategy execution |
| 🛡️ **Risk Management** | Loss limit, position limit, stop loss and position count controls |
| 🤖 **Local LLM** | Optional Ollama integration |
| 🌐 **FastAPI** | Monitoring and API endpoints |
| 📖 **Swagger Docs** | Interactive API documentation |
| 📱 **Telegram** | Optional trading notifications |
| 🧪 **ML / Backtesting** | Machine-learning and backtesting components |
| 🗄️ **Database** | SQLite by default, PostgreSQL supported |
| ⚡ **Redis** | Local Redis support |
| 🐳 **Docker** | PostgreSQL + Redis development environment |
| 🪟 **Windows Scripts** | Automated setup and run scripts |
| 📝 **Logging** | Application logs stored locally |

---

# 🧰 Tech Stack

```text
Python 3.11
│
├── Angel One SmartAPI
├── FastAPI + Uvicorn
├── Pandas + NumPy
├── pandas-ta
├── scikit-learn
├── XGBoost
├── LightGBM
├── SQLAlchemy + SQLite
├── PostgreSQL
├── Redis
├── APScheduler
├── Telegram Bot API
├── Ollama
└── Docker Compose
```

---

# 🚀 Quick Start

## 1️⃣ Requirements

Recommended environment:

- Windows 10/11
- **Python 3.11.x**
- Git
- Internet connection
- Docker Desktop — optional
- Ollama — optional
- Angel One account — only required for broker connectivity

Check your installation:

```bash
python --version
git --version
```

Expected Python version:

```text
Python 3.11.x
```

---

## 2️⃣ Clone

```bash
git clone https://github.com/manish-kuntal/trading-agent.git
cd trading-agent
```

---

## 3️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate on Windows:

```bat
venv\Scripts\activate
```

You should see:

```text
(venv)
```

in your terminal prompt.

---

## 4️⃣ Install Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Main dependencies

| Package | Purpose |
|---|---|
| `smartapi-python` | Angel One SmartAPI |
| `pyotp` | TOTP authentication |
| `websocket-client` | WebSocket market data |
| `python-dotenv` | Environment variables |
| `pydantic-settings` | Configuration |
| `pandas` | Data processing |
| `numpy` | Numerical operations |
| `pandas-ta` | Technical indicators |
| `yfinance` | Market data |
| `scikit-learn` | Machine learning |
| `xgboost` | ML models |
| `lightgbm` | ML models |
| `sqlalchemy` | Database ORM |
| `aiosqlite` | Async SQLite |
| `fastapi` | API server |
| `uvicorn` | ASGI server |
| `apscheduler` | Scheduled jobs |
| `python-telegram-bot` | Telegram notifications |
| `anthropic` | Optional AI integration |
| `httpx` | HTTP client |
| `loguru` | Logging |
| `python-jose` | Authentication/security |
| `pytest` | Testing |

---

# ⚙️ Configuration

## 5️⃣ Create `.env`

Create your local environment file:

```bat
copy .env.example .env
```

Then open:

```text
.env
```

> [!CAUTION]
> **Never commit `.env` to GitHub.**
>
> Your `.env` may contain broker credentials, API keys, Telegram tokens and other secrets.

The repository is configured to ignore `.env`.

---

## 6️⃣ Paper Trading

Start with:

```env
PAPER_TRADING=true
PAPER_CAPITAL=100000.0
```

This uses virtual capital.

Keep paper trading enabled while developing and testing.

---

## 7️⃣ Angel One

Only configure these if broker connectivity is required:

```env
ANGEL_API_KEY=
ANGEL_CLIENT_ID=
ANGEL_PASSWORD=
ANGEL_TOTP_SECRET=
```

Example:

```env
ANGEL_API_KEY=your_api_key
ANGEL_CLIENT_ID=your_client_id
ANGEL_PASSWORD=your_password
ANGEL_TOTP_SECRET=your_totp_secret
```

> [!CAUTION]
> Never put real broker credentials directly inside Python source files.

Never commit:

- API keys
- Passwords
- TOTP secrets
- Access tokens
- Telegram bot tokens
- Production database passwords

---

## 8️⃣ Telegram

Telegram notifications are optional:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Leave them empty if Telegram is not being used.

---

## 9️⃣ Local LLM / Ollama

Optional local LLM configuration:

```env
USE_LOCAL_LLM=true
OLLAMA_MODEL=qwen3:14b
OLLAMA_BASE_URL=http://localhost:11434
```

Check installed models:

```bash
ollama list
```

Run the configured model:

```bash
ollama run qwen3:14b
```

If the local LLM is not required, disable it in your configuration.

---

## 🔐 API Secret

The project includes:

```env
API_SECRET_KEY=change-this-to-random-string-before-deploy
```

For any real deployment, replace this with a strong random secret.

**Never use the example value in production.**

---

# 🪟 Automatic Windows Setup

The repository includes:

```text
scripts/setup.bat
```

Run:

```bat
scripts\setup.bat
```

The setup script:

1. Checks Python 3.11
2. Creates `venv`
3. Activates the environment
4. Upgrades pip
5. Installs dependencies
6. Creates `.env`
7. Creates required directories

After setup:

```bat
venv\Scripts\activate
```

---

# ▶️ Running the System

## 1️⃣ Test Broker Connection

After configuring Angel One credentials:

```bat
scripts\run_test.bat
```

This runs:

```bash
python test_connection.py
```

---

## 2️⃣ Start Trading Agent

Activate the environment:

```bat
venv\Scripts\activate
```

Start:

```bat
scripts\run_agent.bat
```

Or manually:

```bash
python -m agent.main
```

When paper trading is enabled, the agent should display:

```text
MODE: PAPER TRADING (no real money)
```

Stop with:

```text
Ctrl + C
```

Logs are written under:

```text
logs/
```

---

## 3️⃣ Start API Server

Open a **second terminal**.

```bash
cd trading-agent
```

Activate:

```bat
venv\Scripts\activate
```

Start:

```bat
scripts\run_api.bat
```

Or manually:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

# 🌐 API & Swagger

When the API is running:

### Swagger UI

```text
http://localhost:8000/docs
```

### Health Check

```text
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

# 🗄️ Database

The default database is SQLite:

```env
DATABASE_URL=sqlite:///./trading.db
```

The local database file will be:

```text
trading.db
```

PostgreSQL is also supported through Docker Compose.

---

# 🐳 PostgreSQL + Redis

Make sure Docker Desktop is running.

Start:

```bash
docker compose up -d
```

Check:

```bash
docker compose ps
```

Stop:

```bash
docker compose down
```

Services provided:

```text
PostgreSQL
Redis
```

> [!NOTE]
> The included Docker database credentials are intended for local/demo development. Use unique credentials and secrets for production.

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │     Market Data     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Signal / Strategy │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Risk Management   │
                         └──────────┬──────────┘
                                    │
                          ┌─────────┴─────────┐
                          ▼                   ▼
                 ┌────────────────┐  ┌────────────────┐
                 │ Paper Broker   │  │ Angel One      │
                 │                │  │ SmartAPI       │
                 └───────┬────────┘  └───────┬────────┘
                         │                   │
                         └─────────┬─────────┘
                                   ▼
                         ┌─────────────────────┐
                         │ Database / Logging  │
                         └──────────┬──────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
            FastAPI API        Telegram            ML/Logs
```

---

# 📁 Project Structure

```text
trading-agent/
│
├── agent/
│   ├── data/              # Market data + feature engineering
│   ├── strategy/          # Signals + risk management
│   ├── execution/         # Paper + Angel One execution
│   ├── db/                # Database models
│   └── main.py            # Trading agent entry point
│
├── api/
│   ├── routes/            # API endpoints
│   └── main.py            # FastAPI application
│
├── config/
│   └── settings.py        # Application configuration
│
├── ml/                    # ML + backtesting
├── frontend/              # Dashboard/frontend components
├── infra/                 # Deployment/infrastructure
│
├── scripts/
│   ├── setup.bat
│   ├── run_test.bat
│   ├── run_agent.bat
│   └── run_api.bat
│
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── test_connection.py
└── README.md
```

---

# 🛡️ Risk Management

Default configuration:

| Variable | Default | Meaning |
|---|---:|---|
| `PAPER_CAPITAL` | `100000` | Virtual capital |
| `DAILY_LOSS_LIMIT_PCT` | `0.02` | 2% daily loss limit |
| `MAX_POSITION_PCT` | `0.05` | 5% maximum position size |
| `STOP_LOSS_PCT` | `0.015` | 1.5% stop-loss configuration |
| `MAX_OPEN_POSITIONS` | `3` | Maximum simultaneous positions |

> [!WARNING]
> These values are configuration defaults. They do not guarantee that losses will be prevented.

---

# 🔄 Paper Trading → Live Trading

The project starts with:

```env
PAPER_TRADING=true
```

Keep it this way during development.

Before considering live trading, independently test:

- [ ] Authentication
- [ ] Market-data handling
- [ ] Signal generation
- [ ] Position management
- [ ] Risk management
- [ ] Stop-loss handling
- [ ] Order execution
- [ ] Error handling
- [ ] Database operations
- [ ] Logging
- [ ] API security
- [ ] Broker integration

Only after appropriate testing should live mode be considered:

```env
PAPER_TRADING=false
```

> [!CAUTION]
> Live trading can involve real financial loss.

---

# 🧪 Testing

Run the test suite:

```bash
pytest
```

Run the broker connection test:

```bash
python test_connection.py
```

---

# 🧰 Common Commands

<details>
<summary><b>Environment</b></summary>

### Activate

```bat
venv\Scripts\activate
```

### Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Install dependencies

```bash
pip install -r requirements.txt
```

</details>

<details>
<summary><b>Trading Agent</b></summary>

### Start

```bash
python -m agent.main
```

### Stop

```text
Ctrl + C
```

</details>

<details>
<summary><b>API</b></summary>

### Start

```bash
uvicorn api.main:app --reload
```

### Port 8001

```bash
uvicorn api.main:app --reload --port 8001
```

</details>

<details>
<summary><b>Docker</b></summary>

### Start

```bash
docker compose up -d
```

### Check

```bash
docker compose ps
```

### Stop

```bash
docker compose down
```

</details>

---

# 🐛 Troubleshooting

## Python version error

Check:

```bash
python --version
```

The project expects:

```text
Python 3.11.x
```

---

## Virtual environment problem

Recreate it:

```bash
python -m venv venv
```

Then:

```bat
venv\Scripts\activate
```

---

## Dependency installation problem

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## API does not start

Try:

```bash
python -m uvicorn api.main:app --reload
```

If port `8000` is already in use:

```bash
uvicorn api.main:app --reload --port 8001
```

---

## Docker problem

Check:

```bash
docker --version
docker compose version
```

Then:

```bash
docker compose up -d
```

---

## Ollama problem

Check:

```bash
ollama list
```

Then verify that the model configured in `.env` exists.

---

# 🔐 Security

## Before Every GitHub Push

- [ ] No real API keys in source code
- [ ] No broker passwords in source code
- [ ] No TOTP secrets in source code
- [ ] No Telegram bot tokens in source code
- [ ] No production database passwords in source code
- [ ] `.env` is not committed
- [ ] `.gitignore` contains `.env`
- [ ] Production API secret is random
- [ ] Production database credentials are unique
- [ ] Live trading remains disabled during development

> [!CAUTION]
> If a real secret was ever pushed to a public repository, treat it as exposed and rotate/revoke it even after removing it from the current source code.

---

# 🗺️ Roadmap

### Phase 1–3 — Core & Paper Trading

- Core trading engine
- Market data
- Strategy
- Risk management
- Paper trading
- Testing

### Phase 4 — Broker Integration

- Angel One integration
- Controlled live-trading preparation
- Additional safety checks

### Phase 5 — Deployment

- Docker deployment
- VPS deployment
- Production configuration
- Monitoring
- Security hardening

### Phase 6 — Dashboard

- Frontend dashboard
- Mobile monitoring
- Advanced analytics
- Expanded automation

---

# 📌 Project Status

| Component | Status |
|---|---|
| Paper Trading | 🟢 Available |
| Risk Controls | 🟢 Available |
| Angel One Integration | 🟡 Development / Testing |
| FastAPI | 🟢 Available |
| Telegram | 🟡 Optional |
| ML / Backtesting | 🟡 Development |
| Ollama | 🟡 Optional |
| PostgreSQL | 🟢 Supported |
| Redis | 🟢 Supported |
| Docker | 🟢 Supported |
| Mobile Dashboard | 🔵 Roadmap |

---

# ⚠️ Disclaimer

This software is provided for educational and research purposes.

Trading financial instruments involves risk, including the possibility of financial loss.

Users are responsible for:

- Reviewing the source code
- Testing the system
- Protecting credentials
- Configuring risk controls
- Following broker terms
- Following applicable laws and regulations
- Making their own decisions regarding use of the software

---

<div align="center">

## 👨‍💻 Author

**Manish Kuntal**

[GitHub](https://github.com/manish-kuntal) •
[Trading Agent Repository](https://github.com/manish-kuntal/trading-agent)

<br>

**Built with Python • FastAPI • SmartAPI • ML • Local AI**

</div>
