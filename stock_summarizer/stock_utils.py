"""
Utilities for fetching stock data and related context.

Uses yfinance for price/metrics and optionally NewsAPI for recent headlines.

Environment:
- NEWS_API_KEY (optional): If set, fetches related headlines from NewsAPI.

Note: This module is designed to be used both from Streamlit UI and as a tool
for OpenAI Assistants function-calling. Keep outputs concise and robust.
"""

from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests
import yfinance as yf
from dotenv import load_dotenv


load_dotenv()

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")


def _format_currency(value: Optional[float]) -> str:
    if value is None:
        return "-"
    try:
        if abs(value) >= 1e12:
            return f"${value/1e12:.2f}T"
        if abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        if abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        if abs(value) >= 1e3:
            return f"${value/1e3:.2f}K"
        return f"${value:.2f}"
    except Exception:
        return str(value)


def _safe_get(d: Dict[str, Any], key: str, default=None):
    try:
        return d.get(key, default)
    except Exception:
        return default


def fetch_related_headlines(ticker: str, limit: int = 5) -> List[Dict[str, str]]:
    """
    Fetch recent headlines via NewsAPI mentioning the ticker.
    Returns empty list if NEWS_API_KEY isn't set or request fails.
    """
    if not NEWS_API_KEY:
        return []
    url = (
        f"https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API_KEY}&pageSize={limit}&sortBy=publishedAt"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", [])
        items = []
        for a in articles:
            items.append(
                {
                    "title": a.get("title") or "",
                    "source": _safe_get(a.get("source") or {}, "name", ""),
                    "url": a.get("url") or "",
                    "publishedAt": a.get("publishedAt") or "",
                }
            )
        return items
    except Exception:
        return []


def get_stock_snapshot(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d",
) -> str:
    """
    Return a concise multi-line text snapshot of a stock's recent performance and key metrics.

    Intended for LLM consumption. The UI can fetch full history separately for charting.
    """
    t = yf.Ticker(ticker)

    # Price history
    try:
        hist = t.history(period=period, interval=interval)
    except Exception:
        hist = None

    last_price = None
    prev_close = None
    day_high = None
    day_low = None
    year_high = None
    year_low = None
    market_cap = None
    volume = None

    # fast_info is more reliable and quicker than info
    try:
        fi = t.fast_info  # type: ignore[attr-defined]
        last_price = _safe_get(fi, "lastPrice")
        prev_close = _safe_get(fi, "previousClose")
        day_high = _safe_get(fi, "dayHigh")
        day_low = _safe_get(fi, "dayLow")
        year_high = _safe_get(fi, "yearHigh")
        year_low = _safe_get(fi, "yearLow")
        market_cap = _safe_get(fi, "marketCap")
        volume = _safe_get(fi, "lastVolume") or _safe_get(fi, "volume")
    except Exception:
        # Fallback to .info (slower, may be deprecated for some fields)
        try:
            info = t.info
            last_price = info.get("currentPrice") or info.get("regularMarketPrice")
            prev_close = info.get("previousClose")
            day_high = info.get("dayHigh")
            day_low = info.get("dayLow")
            year_high = info.get("fiftyTwoWeekHigh")
            year_low = info.get("fiftyTwoWeekLow")
            market_cap = info.get("marketCap")
            volume = info.get("volume")
        except Exception:
            pass

    change = None
    pct_change = None
    try:
        if last_price is not None and prev_close is not None and prev_close != 0:
            change = last_price - prev_close
            pct_change = (change / prev_close) * 100
    except Exception:
        pass

    # Headlines (optional)
    headlines = fetch_related_headlines(ticker, limit=3)

    # Build a clean, concise text snapshot for the LLM
    lines = []
    lines.append(f"Symbol: {ticker.upper()}")
    if last_price is not None:
        if pct_change is not None and change is not None:
            sign = "+" if change >= 0 else ""
            lines.append(
                f"Last: {_format_currency(last_price)} ({sign}{change:.2f}, {sign}{pct_change:.2f}%)"
            )
        else:
            lines.append(f"Last: {_format_currency(last_price)}")
    if day_low is not None and day_high is not None:
        lines.append(f"Day range: {_format_currency(day_low)} - {_format_currency(day_high)}")
    if year_low is not None and year_high is not None:
        lines.append(
            f"52W range: {_format_currency(year_low)} - {_format_currency(year_high)}"
        )
    if market_cap is not None:
        lines.append(f"Market cap: {_format_currency(market_cap)}")
    if volume is not None:
        try:
            lines.append(f"Volume: {int(volume):,}")
        except Exception:
            lines.append(f"Volume: {volume}")

    if hist is not None and not hist.empty:
        try:
            start_dt = hist.index[0].strftime("%Y-%m-%d")
            end_dt = hist.index[-1].strftime("%Y-%m-%d")
            lines.append(f"History window: {start_dt} -> {end_dt} ({period}, {interval})")
            # Provide a couple of points for context
            start_close = float(hist["Close"].iloc[0])
            end_close = float(hist["Close"].iloc[-1])
            delta = end_close - start_close
            pct = (delta / start_close) * 100 if start_close else 0.0
            sign2 = "+" if delta >= 0 else ""
            lines.append(
                f"Period change: {sign2}{delta:.2f} ({sign2}{pct:.2f}%) from {_format_currency(start_close)} to {_format_currency(end_close)}"
            )
        except Exception:
            pass

    if headlines:
        lines.append("Headlines:")
        for h in headlines:
            ts = h.get("publishedAt") or ""
            try:
                ts_fmt = (
                    datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                    if ts
                    else ""
                )
            except Exception:
                ts_fmt = ts or ""
            title = h.get("title") or ""
            source = h.get("source") or ""
            lines.append(f"- {ts_fmt} | {source}: {title}")

    return "\n".join(lines)


__all__ = ["get_stock_snapshot", "fetch_related_headlines"]
