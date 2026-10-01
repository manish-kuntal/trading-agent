from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Broker
    angel_api_key:     str   = ""
    angel_client_id:   str   = ""
    angel_password:    str   = ""
    angel_totp_secret: str   = ""

    # Database
    database_url:      str   = "sqlite:///./trading.db"

    # Redis
    redis_url:         str   = "redis://localhost:6379"

    # Trading mode
    paper_trading:     bool  = True
    paper_capital:     float = 100_000.0   # ₹1 lakh virtual capital

    # Risk parameters
    daily_loss_limit_pct:  float = 0.02   # 2%  of capital
    max_position_pct:      float = 0.05   # 5%  per trade
    stop_loss_pct:         float = 0.015  # 1.5% SL
    max_open_positions:    int   = 3

    # Square-off time (IST)
    square_off_hour:   int = 15
    square_off_minute: int = 15

    # LLM filter
    gemini_api_key: str  = "YOUR API"
    gemini_model:   str  = "gemini-1.5-flash"
    use_gemini:     bool = False

    # API server
    api_secret_key:    str  = "change-this"
    api_host:          str  = "0.0.0.0"
    api_port:          int  = 8000

    # Notifications
    telegram_bot_token: str = ""
    telegram_chat_id:   str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
