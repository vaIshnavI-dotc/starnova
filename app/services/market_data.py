import os
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SECTOR_MAP = {
    # Auto
    "TATAMOTORS": "auto", "MARUTI": "auto", "M&M": "auto", "BAJAJ-AUTO": "auto",
    "HEROMOTOCO": "auto", "TVSMOTOR": "auto", "EICHERMOT": "auto",
    # FMCG
    "HINDUNILVR": "fmcg", "ITC": "fmcg", "NESTLEIND": "fmcg", "BRITANNIA": "fmcg",
    "DABUR": "fmcg", "MARICO": "fmcg", "TATACONSUM": "fmcg", "GODREJCP": "fmcg",
    # Banking
    "HDFCBANK": "banking", "ICICIBANK": "banking", "SBIN": "banking",
    "KOTAKBANK": "banking", "AXISBANK": "banking", "INDUSINDBK": "banking",
    # IT
    "TCS": "it", "INFY": "it", "WIPRO": "it", "HCLTECH": "it",
    "TECHM": "it", "LTIM": "it", "PERSISTENT": "it",
    # Pharma
    "SUNPHARMA": "pharma", "CIPLA": "pharma", "DRREDDY": "pharma",
    "DIVISLAB": "pharma", "LUPIN": "pharma", "APOLLOHOSP": "pharma",
    # Energy
    "RELIANCE": "energy", "ONGC": "energy", "IOC": "energy", "BPCL": "energy",
    "NTPC": "energy", "POWERGRID": "energy", "TATAPOWER": "energy", "ADANIGREEN": "energy",
    # Metals
    "TATASTEEL": "metals", "JSWSTEEL": "metals", "HINDALCO": "metals",
    "VEDL": "metals", "JINDALSTEL": "metals", "SAIL": "metals",
}

STOCK_NAMES = {
    "TATAMOTORS": "Tata Motors",
    "MARUTI": "Maruti Suzuki",
    "M&M": "Mahindra & Mahindra",
    "HDFCBANK": "HDFC Bank",
    "ICICIBANK": "ICICI Bank",
    "SBIN": "State Bank of India",
    "TCS": "Tata Consultancy Services",
    "INFY": "Infosys",
    "WIPRO": "Wipro",
    "SUNPHARMA": "Sun Pharmaceutical",
    "CIPLA": "Cipla",
    "RELIANCE": "Reliance Industries",
    "TATASTEEL": "Tata Steel",
    "HINDUNILVR": "Hindustan Unilever",
    "ITC": "ITC Limited",
    "ZOMATO": "Zomato",
    "BEL": "Bharat Electronics",
    "HAL": "Hindustan Aeronautics",
    "BHEL": "Bharat Heavy Electricals",
    "SUZLON": "Suzlon Energy",
    "IREDA": "Indian Renewable Energy Development Agency",
    "RPOWER": "Reliance Power",
    "IDEA": "Vodafone Idea",
    "YESBANK": "Yes Bank",
}

FALLBACK_PRICES = {
    "TATAMOTORS": (812.4, 6.2, "Already up 6.2% in the last 7 days."),
    "BEL": (304.5, 3.8, "Up 3.8% over the past 7 sessions."),
    "INFY": (1840.0, 1.5, "Trading in a narrow 1.5% range over 7 days."),
    "ZOMATO": (265.0, -2.4, "Down 2.4% over the last 7 days."),
    "SUZLON": (58.4, 10.1, "Strong recent rally of 10.1% over 7 days."),
    "HAL": (4650.0, 4.2, "Up 4.2% over the last 7 days."),
    "BHEL": (295.0, -1.8, "Down 1.8% over the last 7 days."),
    "IREDA": (215.0, 11.2, "Up 11.2% in the last 7 days."),
    "RPOWER": (39.0, 9.5, "Up 9.5% in the last 7 days."),
    "IDEA": (15.2, 8.4, "Up 8.4% in the last 7 days."),
    "YESBANK": (23.5, 1.2, "Flat over the last 7 days."),
    "TCS": (3980.0, 2.1, "Up 2.1% over the last 7 days."),
}


def get_stock_name(ticker: str) -> str:
    cleaned = ticker.upper().replace(".NS", "").replace(".BO", "")
    return STOCK_NAMES.get(cleaned, cleaned)


def get_ticker_sector(ticker: str) -> str:
    cleaned = ticker.upper().replace(".NS", "").replace(".BO", "")
    return SECTOR_MAP.get(cleaned, "other")


def get_price_and_7d_change(ticker: str) -> Tuple[Optional[float], Optional[float], str]:
    cleaned = ticker.upper().replace(".NS", "").replace(".BO", "")
    mode = os.getenv("LLM_MODE", "mock").lower()

    # In mock mode, immediately return deterministic data without network delays
    if mode == "mock":
        if cleaned in FALLBACK_PRICES:
            return FALLBACK_PRICES[cleaned]
        return 500.0, 3.0, "Up 3.0% in the last 7 days."

    symbol = f"{cleaned}.NS"
    try:
        import yfinance as yf
        data = yf.Ticker(symbol).history(period="10d")
        if not data.empty and len(data) >= 2:
            price_now = round(float(data["Close"].iloc[-1]), 2)
            idx = 0 if len(data) <= 6 else -6
            price_7d_ago = float(data["Close"].iloc[idx])
            change_7d = round(((price_now - price_7d_ago) / price_7d_ago) * 100.0, 1)

            if change_7d > 5.0:
                note = f"Already up {change_7d}% in the last 7 days."
            elif change_7d < -5.0:
                note = f"Down {abs(change_7d)}% in the last 7 days."
            else:
                note = f"Price has moved {change_7d}% over the last 7 days."

            return price_now, change_7d, note
    except Exception as e:
        logger.warning(f"yfinance lookup failed for {symbol}: {e}")

    if cleaned in FALLBACK_PRICES:
        return FALLBACK_PRICES[cleaned]

    return 500.0, 0.0, "Recent 7-day price data unavailable."
