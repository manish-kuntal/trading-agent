import os
import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect
from loguru import logger
from .base_broker import BaseBroker

load_dotenv()


class AngelBroker(BaseBroker):
    """Live broker — Angel One SmartAPI. Phase 4+."""

    def __init__(self):
        self.api_key      = os.getenv("ANGEL_API_KEY")
        self.client_id    = os.getenv("ANGEL_CLIENT_ID")
        self.password     = os.getenv("ANGEL_PASSWORD")
        self.totp_secret  = os.getenv("ANGEL_TOTP_SECRET")
        self.obj          = None
        self.jwt_token    = None
        self.feed_token   = None
        self.refresh_token= None

    # ------------------------------------------------------------------
    # AUTH
    # ------------------------------------------------------------------
    def login(self) -> bool:
        """Call daily at 9:00 AM IST via scheduler."""
        try:
            totp = pyotp.TOTP(self.totp_secret).now()
            self.obj = SmartConnect(api_key=self.api_key)
            data = self.obj.generateSession(self.client_id, self.password, totp)
            if data["status"]:
                self.jwt_token   = data["data"]["jwtToken"]
                self.refresh_token= data["data"]["refreshToken"]
                self.feed_token  = self.obj.getfeedToken()
                logger.info(f"[Angel] Login OK — client: {self.client_id}")
                return True
            logger.error(f"[Angel] Login failed: {data.get('message')}")
            return False
        except Exception as e:
            logger.error(f"[Angel] Login exception: {e}")
            return False

    # ------------------------------------------------------------------
    # MARKET DATA
    # ------------------------------------------------------------------
    def get_ltp(self, exchange: str, symbol: str, token: str) -> float:
        data = self.obj.ltpData(exchange, symbol, token)
        return float(data["data"]["ltp"])

    def get_candles(self, token: str, interval: str,
                    from_date: str, to_date: str) -> list:
        """
        interval: ONE_MINUTE | FIVE_MINUTE | FIFTEEN_MINUTE |
                  THIRTY_MINUTE | ONE_HOUR | ONE_DAY
        from_date / to_date: "YYYY-MM-DD HH:MM"
        returns: [[timestamp, open, high, low, close, volume], ...]
        """
        params = {
            "exchange":    "NSE",
            "symboltoken": token,
            "interval":    interval,
            "fromdate":    from_date,
            "todate":      to_date,
        }
        data = self.obj.getCandleData(params)
        return data["data"]

    # ------------------------------------------------------------------
    # ORDERS
    # ------------------------------------------------------------------
    def place_order(self, symbol: str, token: str,
                    action: str, qty: int) -> str:
        """Market MIS order. Returns order_id."""
        params = {
            "variety":        "NORMAL",
            "tradingsymbol":  symbol,
            "symboltoken":    token,
            "transactiontype": action,   # BUY | SELL
            "exchange":       "NSE",
            "ordertype":      "MARKET",
            "producttype":    "MIS",     # Intraday only
            "duration":       "DAY",
            "price":          "0",
            "quantity":       str(qty),
        }
        resp = self.obj.placeOrder(params)
        order_id = resp["data"]["orderid"]
        logger.info(f"[Angel] Order → {action} {qty}x {symbol} | id={order_id}")
        return order_id

    def place_stoploss(self, symbol: str, token: str, action: str,
                       qty: int, trigger: float, price: float) -> str:
        """SL-Limit order. Place immediately after entry."""
        params = {
            "variety":        "STOPLOSS",
            "tradingsymbol":  symbol,
            "symboltoken":    token,
            "transactiontype": action,
            "exchange":       "NSE",
            "ordertype":      "STOPLOSS_LIMIT",
            "producttype":    "MIS",
            "duration":       "DAY",
            "price":          str(price),
            "triggerprice":   str(trigger),
            "quantity":       str(qty),
        }
        resp = self.obj.placeOrder(params)
        sl_id = resp["data"]["orderid"]
        logger.info(f"[Angel] SL order → {symbol} trigger=₹{trigger} | id={sl_id}")
        return sl_id

    def cancel_order(self, order_id: str) -> bool:
        resp = self.obj.cancelOrder(order_id, "NORMAL")
        return bool(resp["status"])

    def get_order_status(self, order_id: str) -> dict:
        orders = self.obj.orderBook()
        for o in (orders["data"] or []):
            if o["orderid"] == order_id:
                return o
        return {}

    # ------------------------------------------------------------------
    # POSITIONS
    # ------------------------------------------------------------------
    def get_positions(self) -> list:
        data = self.obj.position()
        return data["data"] or []

    def close_all_positions(self):
        """Square-off all open MIS positions. Call at 3:15 PM IST."""
        positions = self.get_positions()
        for pos in positions:
            net = int(pos.get("netqty", 0))
            if net != 0:
                action = "SELL" if net > 0 else "BUY"
                self.place_order(
                    pos["tradingsymbol"], pos["symboltoken"],
                    action, abs(net)
                )
                logger.info(f"[Angel] Square-off → {action} {abs(net)}x {pos['tradingsymbol']}")
