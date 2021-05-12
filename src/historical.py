from re import S, search
from alpaca_trade_api.rest import *
from datetime import datetime, timedelta
from time import sleep
from abraham3k import Abraham
import pandas as pd
from multiprocessing import Pool, Process
import random
from bowl import Bowl

# Data viz
import plotly.graph_objs as go

DTFORMAT = "%Y-%m-%dT%H:%M:%SZ"

api_key = open("keys/alpaca_paper_public").read().strip()
api_secret = open("keys/alpaca_paper_private").read().strip()
base_url = "https://paper-api.alpaca.markets"

alpaca = REST(
    key_id=api_key, secret_key=api_secret, base_url=base_url, api_version="v2"
)

# abraham = Abraham(
#    news_source="newsapi",
#    newsapi_key=open("keys/newsapi-public-2").read().strip(),
#    bearer_token=open("keys/twitter-bearer-token").read().strip(),
# )

if __name__ == "__main__":
    tickers = [
        "tsla",
        "goog",
        "gld",
        "spy",
        "bdry",
        "msft",
        "nvda",
        "amd",
        "iht",
        "aapl",
        "fb",
        "brk.a",
    ]
    random.shuffle(tickers)
    days = 2

    for ticker in tickers:
        print(f"[{ticker}]")
        df = alpaca.get_bars(
            ticker,
            TimeFrame.Minute,
            (datetime.now() - timedelta(hours=24 * days)).strftime(DTFORMAT),
            datetime.now().strftime(DTFORMAT),
            adjustment="raw",
        ).df
        bowler = Bowl()
        bowler.scipy_opt(df["close"])
        bowler.backtest(df["close"], loud=True)
