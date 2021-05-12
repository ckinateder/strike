from os import stat
from re import S, search
from alpaca_trade_api.rest import *
from datetime import datetime, timedelta
from time import sleep
from abraham3k import Abraham
import pandas as pd
from multiprocessing import Pool, Process
import random
from bowl import Bowl
import logging

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
# Data viz
import plotly.graph_objs as go

DTFORMAT = "%Y-%m-%dT%H:%M:%SZ"

api_key = open("keys/alpaca_paper_public").read().strip()
api_secret = open("keys/alpaca_paper_private").read().strip()
base_url = "https://paper-api.alpaca.markets"

# abraham = Abraham(
#    news_source="newsapi",
#    newsapi_key=open("keys/newsapi-public-2").read().strip(),
#    bearer_token=open("keys/twitter-bearer-token").read().strip(),
# )


class Alpaca:
    def __init__(
        self,
        api_key=open("keys/alpaca_paper_public").read().strip(),
        api_secret=open("keys/alpaca_paper_private").read().strip(),
        base_url="https://paper-api.alpaca.markets",
    ) -> None:
        self.api = REST(
            key_id=api_key, secret_key=api_secret, base_url=base_url, api_version="v2"
        )

    def get_bars(
        self, ticker, timeframe=TimeFrame.Minute, how_far_back=timedelta(hours=24)
    ):
        """Wrapper for the api to simplify the calls

        Params
        ------
        ticker : str
            ticker to search for
        timeframe : TimeFrame = TimeFrame.Minute
            the timeframe
        how_far_back : timedelta = timedelta(hours=24)
            how far back from now to search for

        Returns
        -------
        df : pd.DataFrame
        """
        df = self.api.get_bars(
            ticker,
            TimeFrame.Minute,
            (datetime.now() - how_far_back).strftime(DTFORMAT),
            datetime.now().strftime(DTFORMAT),
            adjustment="raw",
        ).df
        return df

    def submit_limit_order(self, ticker, side, price, qty=1, time_in_force="day"):
        """Submit a limit order

        Params
        ------
        ticker : str
            ticker to act on
        side : str
            buy or sell
        price : float
            price to buy at
        qty : int
            how many shares to sell/buy
        time_in_force : str
            expire timne

        Returns
        -------
        True
        """
        self.api.submit_order(
            symbol=ticker,
            qty=qty,  # fractional shares
            side=side,
            type="limit",
            limit_price=price,
            time_in_force=time_in_force,
        )
        return True

    def submit_market_order(self, ticker, side, qty=1, time_in_force="day"):
        """Submit a market order

        Params
        ------
        ticker : str
            ticker to act on
        side : str
            buy or sell
        qty : int
            how many shares to sell/buy
        time_in_force : str
            expire timne

        Returns
        -------
        True
        """
        self.api.submit_order(
            symbol=ticker,
            qty=qty,  # fractional shares
            side=side,
            type="market",
            time_in_force=time_in_force,
        )
        return True

    def get_account(self):
        """
        Get account info
        """
        return self.api.get_account()

    def any_open_orders(self) -> bool:
        """
        Returns true if any open orders
        """
        resp = self.api.list_orders(status="open")
        return len(resp) > 0

    def get_position(self, ticker):
        """Gets the position for a ticker"""
        return self.api.get_position(ticker)

    def get_shares(self, ticker):
        """Returns the share count that you possess for a ticker"""
        try:
            return self.api.get_position(ticker)["qty"]
        except Exception as e:
            logging.warning(f"Issue getting position for {ticker} (e)")
            return 0


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

    alpaca = Alpaca()

    bowler = Bowl(window=5, sigma=1.77)
    for ticker in tickers:
        print(f"[{ticker}]")
        # bowler.optimize(df["close"])
        df = alpaca.get_bars(ticker)
        bowler.backtest(df["close"], loud=True)
