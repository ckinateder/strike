# cycles between predicting/making trades
from bowl import Bowl
from alpaca import Alpaca
import threading
import pandas as pd
from time import sleep
from datetime import datetime
import logging, math

logger = logging.getLogger(__name__)


class Cycler:
    def __init__(
        self,
        api_key=open("keys/alpaca_paper_public").read().strip(),
        api_secret=open("keys/alpaca_paper_private").read().strip(),
        base_url="https://paper-api.alpaca.markets",
    ) -> None:
        self.bowl = Bowl()
        self.alpaca = Alpaca(api_key, api_secret, base_url)

    def trade(self, ticker, side, price, qty):
        """Trades if all checks pass"""
        buying_power = self.alpaca.get_buying_power()
        num_shares = self.alpaca.get_shares(ticker)
        open_trades = self.alpaca.any_open_orders()

        if not open_trades:
            if side == "buy":
                if buying_power >= price * qty:
                    self.alpaca.submit_limit_order(
                        ticker=ticker, side=side, price=price, qty=qty
                    )
                    return True
                else:
                    logger.warning(
                        f"Not enough balance to buy ({buying_power} < {price*qty})"
                    )
            elif side == "sell":
                if num_shares >= qty:
                    self.alpaca.submit_limit_order(
                        ticker=ticker, side=side, price=price, qty=qty
                    )
                    return True
                else:
                    logger.warning(f"Not enough shares to sell ({num_shares} < {qty})")
            elif side == "hold":  # do nothing
                return True
        else:
            logger.warning("Open trades... not trading")
            return False
        return False

    def cycle(self, ticker, spend_amt=1000):
        """
        Cycles between predicting and trading

        Params
        ------
        ticker : str
            stock ticker
        spend_amt : int = 1000
            max amount of money to spend
        """
        # sleep(60 - datetime.now().second)  # sleep til next min starts
        while True:
            # get the data
            df = self.alpaca.get_bars(ticker)
            close = df.close
            price = close[-1]
            qty = math.floor(spend_amt / price)

            # make a decision
            signal = self.bowl.generate_signal(close, loud=True)

            # act
            self.trade(ticker, signal, price, qty)
            # sleep til next min start
            sleep(60 - datetime.now().second)
