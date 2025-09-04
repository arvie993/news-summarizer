"""
Stock Summarizer Application (Streamlit)

Enter a stock ticker to fetch a quick snapshot and an AI-written summary of recent performance.

Features:
- Uses yfinance to fetch price data and key metrics
- Optionally fetches related headlines via NewsAPI
- Renders an interactive price chart (Plotly)
- Uses OpenAI Assistants API v2 via function-calling to write a concise summary

Environment:
- OPENAI_API_KEY (required)
- NEWS_API_KEY (optional)
"""

import os
import time
import json
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import openai
import yfinance as yf

from .stock_utils import get_stock_snapshot


load_dotenv()

# Initialize OpenAI
client = openai.OpenAI()
if not hasattr(client, "_default_headers"):
    client._default_headers = {}
client._default_headers["OpenAI-Beta"] = "assistants=v2"

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def fetch_history_df(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    t = yf.Ticker(ticker)
    try:
        df = t.history(period=period, interval=interval)
        return df
    except Exception:
        return pd.DataFrame()


def run_assistant_with_snapshot(ticker: str, period: str, interval: str) -> str:
    """Create an assistant, pass the request, and return an AI-generated summary."""
    # Create assistant
    assistant = client.beta.assistants.create(
        name="Stock Summarizer",
        instructions=(
            "You are a helpful financial analyst. Use the provided tool to obtain a concise "
            "snapshot for a ticker, then write a short, plain-English summary (5-8 bullets) covering "
            "overall trend, key levels, and noteworthy headlines if available. Avoid speculation."
        ),
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_stock_snapshot",
                    "description": "Get a concise stock snapshot for a ticker.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {"type": "string"},
                            "period": {"type": "string"},
                            "interval": {"type": "string"},
                        },
                        "required": ["ticker", "period", "interval"],
                    },
                },
            }
        ],
        model=MODEL,
        extra_headers={"OpenAI-Beta": "assistants=v2"},
    )

    # Create thread
    thread = client.beta.threads.create(extra_headers={"OpenAI-Beta": "assistants=v2"})

    # Add user message
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=(
            f"Please analyze {ticker.upper()} using the tool and provide a concise summary. "
            f"Use period={period}, interval={interval}."
        ),
        extra_headers={"OpenAI-Beta": "assistants=v2"},
    )

    # Start run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Call the tool first, then produce the summary.",
        extra_headers={"OpenAI-Beta": "assistants=v2"},
    )

    # Wait loop and handle tool calls
    summary_text = None
    while True:
        time.sleep(2)
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id, extra_headers={"OpenAI-Beta": "assistants=v2"}
        )
        if run_status.status == "completed":
            # Get final message
            msgs = client.beta.threads.messages.list(
                thread_id=thread.id, extra_headers={"OpenAI-Beta": "assistants=v2"}
            )
            latest = msgs.data[0]
            summary_text = latest.content[0].text.value
            break
        if run_status.status == "requires_action":
            # Execute tool calls
            required = run_status.required_action.submit_tool_outputs.model_dump()
            tool_outputs = []
            for tc in required.get("tool_calls", []):
                if tc["function"]["name"] == "get_stock_snapshot":
                    args = json.loads(tc["function"]["arguments"])
                    output = get_stock_snapshot(
                        ticker=args.get("ticker", ticker),
                        period=args.get("period", period),
                        interval=args.get("interval", interval),
                    )
                    tool_outputs.append({"tool_call_id": tc["id"], "output": output})
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs,
                extra_headers={"OpenAI-Beta": "assistants=v2"},
            )

    return summary_text or ""


def main():
    st.set_page_config(page_title="Stock Summarizer", page_icon="📈", layout="centered")
    st.title("📈 Stock Summarizer")
    st.caption("Enter a ticker to see a chart and an AI-written snapshot summary.")

    with st.form("stock_form"):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            ticker = st.text_input("Ticker", value="AAPL").strip()
        with col2:
            period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
        with col3:
            interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)

        submitted = st.form_submit_button("Analyze")

    if submitted:
        if not ticker:
            st.error("Please enter a valid ticker symbol.")
            return

        with st.spinner("Fetching data and generating summary..."):
            df = fetch_history_df(ticker, period=period, interval=interval)

        if df.empty:
            st.error("Could not fetch price data. Please check the ticker or try again later.")
            return

        # Chart
        fig = px.line(df.reset_index(), x="Date", y="Close", title=f"{ticker.upper()} Close Price")
        st.plotly_chart(fig, use_container_width=True)

        # AI Summary
        with st.spinner("Calling AI assistant..."):
            summary = run_assistant_with_snapshot(ticker, period, interval)
        if summary:
            st.subheader("AI Summary")
            st.write(summary)
        else:
            st.warning("No summary returned.")


if __name__ == "__main__":
    main()
