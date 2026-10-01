AI Intraday Trading Agent

An autonomous NSE/BSE intraday trading system built with Python, featuring paper trading, risk management, Angel One SmartAPI integration, market-data processing, FastAPI monitoring, Telegram notifications, ML/backtesting components, and optional local LLM support.

«Important: This project is intended for educational and research purposes. Paper trading is enabled by default. Do not use real money until the complete system has been independently tested and reviewed.»

---

Features

- Paper trading with virtual capital
- Angel One SmartAPI integration
- NIFTY 50 watchlist
- Automated scheduled strategy execution
- Risk management
- Daily loss limit
- Position-size limit
- Stop-loss configuration
- Maximum open positions
- Market data processing
- Techachha ise laptop se hi kese replace karu usse
- nical indicators
- ML and backtesting components
- FastAPI monitoring API
- Swagger API documentation
- Telegram notifications
- SQLite database
- PostgreSQL support
- Redis support
- Docker Compose support
- Optional local LLM with Ollama
- Windows setup scripts
- Application logging

---

Requirements

Recommended Environment

- Windows 10/11
- Python 3.11.x
- Git
- Internet connection
- Docker Desktop — optional
- Ollama — optional
- Angel One account — only required for broker integration

Check your installation:

python --version
git --version

Python should show:

Python 3.11.x

---

1. Clone the Repository

Open Command Prompt / PowerShell / Git Bash:

git clone https://github.com/manish-kuntal/trading-agent.git

Enter the project:

cd trading-agent

---

2. Create Virtual Environment

Create the Python virtual environment:

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

You should now see something similar to:

(venv)

before your terminal path.

---

3. Install Dependencies

Upgrade pip:

python -m pip install --upgrade pip

Install all project dependencies:

pip install -r requirements.txt

The main dependencies include:

Package| Purpose
"smartapi-python"| Angel One SmartAPI
"pyotp"| TOTP authentication
"websocket-client"| WebSocket market data
"python-dotenv"| Environment variables
"pydantic-settings"| Configuration management
"pandas"| Data processing
"numpy"| Numerical operations
"pandas-ta"| Technical indicators
"yfinance"| Market data
"scikit-learn"| Machine learning
"xgboost"| ML models
"lightgbm"| ML models
"sqlalchemy"| Database ORM
"aiosqlite"| Async SQLite
"fastapi"| API server
"uvicorn"| FastAPI server
"apscheduler"| Scheduled jobs
"python-telegram-bot"| Telegram notifications
"anthropic"| Optional AI integration
"httpx"| HTTP client
"loguru"| Logging
"python-jose"| Authentication/security
"pytest"| Testing

---

4. Configure ".env"

The project uses environment variables for credentials and configuration.

Create ".env" from the example:

copy .env.example .env

Or manually create ".env".

Important

Never upload your real ".env" file to GitHub.

The repository already ignores ".env" through ".gitignore".

---

5. Paper Trading Configuration

For development, keep:

PAPER_TRADING=true
PAPER_CAPITAL=100000.0

This means the system uses virtual capital instead of real money.

Recommended starting mode:

PAPER TRADING

Do not enable live trading while you are still testing the system.

---

6. Angel One Configuration

If you want to test Angel One broker connectivity, configure:

ANGEL_API_KEY=
ANGEL_CLIENT_ID=
ANGEL_PASSWORD=
ANGEL_TOTP_SECRET=

Fill these values with your own credentials.

Example:

ANGEL_API_KEY=your_api_key
ANGEL_CLIENT_ID=your_client_id
ANGEL_PASSWORD=your_password
ANGEL_TOTP_SECRET=your_totp_secret

Security

Never put real credentials directly inside Python files.

Never commit:

- API keys
- Passwords
- TOTP secrets
- Access tokens
- Telegram bot tokens
- Database production passwords

---

7. Telegram Notifications

Telegram is optional.

Configure:

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

If Telegram is not required, leave them empty.

---

8. Local LLM / Ollama

The project can optionally use a local LLM.

Configuration:

USE_LOCAL_LLM=true
OLLAMA_MODEL=qwen3:14b
OLLAMA_BASE_URL=http://localhost:11434

If you are using Ollama, make sure Ollama is installed and the model exists.

Check models:

ollama list

Example:

ollama run qwen3:14b

If you don't want to use the local LLM, disable it in your configuration.

---

9. API Secret

The API has a configurable secret:

API_SECRET_KEY=change-this-to-random-string-before-deploy

For any real deployment, replace it with a long random value.

Do not use the example value in production.

---

10. Automatic Windows Setup

The repository includes:

scripts/setup.bat

You can use it instead of manually creating the environment.

Run:

scripts\setup.bat

The script:

1. Checks Python 3.11
2. Creates "venv"
3. Activates the environment
4. Upgrades pip
5. Installs dependencies
6. Creates ".env"
7. Creates required directories

After setup, activate the environment:

venv\Scripts\activate

---

11. Test the Connection

Run:

scripts\run_test.bat

This executes:

python test_connection.py

Use this when Angel One credentials are configured.

---

12. Run the Trading Agent

Make sure the virtual environment is active:

venv\Scripts\activate

Start the agent:

scripts\run_agent.bat

Or manually:

python -m agent.main

When paper trading is enabled, you should see:

MODE: PAPER TRADING (no real money)

The agent then starts its scheduler and strategy system.

Stop the agent with:

Ctrl + C

---

13. Run the API Server

Open a second terminal.

Go to the project:

cd trading-agent

Activate the environment:

venv\Scripts\activate

Start the API:

scripts\run_api.bat

Or manually:

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

---

14. API Documentation

Once the API is running, open:

http://localhost:8000/docs

This opens the FastAPI Swagger interface.

Health check:

http://localhost:8000/health

Expected response:

{
  "status": "ok"
}

---

15. Database

The default database is SQLite:

DATABASE_URL=sqlite:///./trading.db

The database file will be created locally:

trading.db

For local PostgreSQL development, Docker Compose is also provided.

---

16. PostgreSQL + Redis with Docker

Make sure Docker Desktop is running.

Start services:

docker compose up -d

Check services:

docker compose ps

Stop services:

docker compose down

The Docker configuration currently provides:

PostgreSQL
Redis

The included database credentials are intended for local/demo development.

For production, use unique credentials stored through environment variables/secrets.

---

17. Project Structure

trading-agent/
│
├── agent/
│   ├── data/
│   │   └── Market data + feature engineering
│   │
│   ├── strategy/
│   │   └── Signals + risk management
│   │
│   ├── execution/
│   │   └── Paper + Angel One execution
│   │
│   ├── db/
│   │   └── Database models
│   │
│   └── main.py
│       └── Trading agent entry point
│
├── api/
│   ├── routes/
│   │   └── API endpoints
│   │
│   └── main.py
│       └── FastAPI application
│
├── config/
│   └── settings.py
│       └── Application configuration
│
├── ml/
│   └── Model training + backtesting
│
├── frontend/
│   └── Dashboard/frontend components
│
├── infra/
│   └── Deployment/infrastructure
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

---

18. Risk Management

Default risk configuration:

Variable| Default| Meaning
"PAPER_CAPITAL"| "100000"| Virtual capital
"DAILY_LOSS_LIMIT_PCT"| "0.02"| 2% daily loss limit
"MAX_POSITION_PCT"| "0.05"| 5% maximum position size
"STOP_LOSS_PCT"| "0.015"| 1.5% stop-loss configuration
"MAX_OPEN_POSITIONS"| "3"| Maximum simultaneous positions

These are configuration values, not guarantees against losses.

---

19. Paper Trading → Live Trading

The project is designed to start with:

PAPER_TRADING=true

Keep paper trading enabled while developing and testing.

Only after independently testing:

- Authentication
- Market data
- Signal generation
- Position management
- Risk management
- Stop-loss handling
- Order execution
- Error handling
- Database operations
- Logging
- API security
- Broker integration

should you consider changing:

PAPER_TRADING=false

Live trading can involve real financial loss.

---

20. Common Commands

Activate environment

venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Upgrade pip

python -m pip install --upgrade pip

Run tests

pytest

Run connection test

python test_connection.py

Run trading agent

python -m agent.main

Run API

uvicorn api.main:app --reload

Run API on another port

uvicorn api.main:app --reload --port 8001

Start Docker

docker compose up -d

Stop Docker

docker compose down

---

21. Troubleshooting

Python version error

Check:

python --version

The project expects:

Python 3.11.x

---

Virtual environment not working

Recreate it:

python -m venv venv

Then:

venv\Scripts\activate

---

Dependency installation error

Run:

python -m pip install --upgrade pip

Then:

pip install -r requirements.txt

---

API does not start

Try:

python -m uvicorn api.main:app --reload

If port "8000" is busy:

uvicorn api.main:app --reload --port 8001

---

Docker is not working

Check:

docker --version
docker compose version

Then:

docker compose up -d

---

Ollama is not responding

Check:

ollama list

Then verify the model configured in ".env" exists.

---

22. Security Checklist

Before every GitHub push:

- [ ] No real API keys in source code
- [ ] No broker passwords in source code
- [ ] No TOTP secrets in source code
- [ ] No Telegram bot tokens in source code
- [ ] No production database passwords in source code
- [ ] ".env" is not committed
- [ ] ".gitignore" contains ".env"
- [ ] Production API secret is random
- [ ] Production database credentials are unique
- [ ] Live trading is disabled during development

If a real secret has ever been pushed to a public repository, consider it exposed and rotate/revoke it, even if the current file has been cleaned.

---

23. Development Roadmap

Phase 1–3

- Core trading engine
- Market data
- Strategy
- Risk management
- Paper trading
- Testing

Phase 4

- Angel One integration
- Live trading preparation
- Additional safety checks

Phase 5

- Docker deployment
- VPS deployment
- Production configuration
- Monitoring
- Security hardening

Phase 6

- Frontend dashboard
- Mobile monitoring
- Advanced analytics
- Expanded automation

---

Disclaimer

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

Author

Manish Kuntal

GitHub:

"https://github.com/manish-kuntal" (https://github.com/manish-kuntal)

Repository:

"https://github.com/manish-kuntal/trading-agent" (https://github.com/manish-kuntal/trading-agent)