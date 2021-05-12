import pandas as pd
import numpy as np
from tqdm import trange

# Data viz
import plotly.graph_objs as go
from scipy.optimize import minimize


class Bowl:
    def __init__(self, window=5, sigma=1.78) -> None:
        self.window = window
        self.sigma = sigma

    def create_bands(self, series: pd.Series, window, sigma):
        """
        Create bowlinger bands
        """
        data = pd.DataFrame(series)
        data["middle"] = series.rolling(window=window).mean()
        data["upper"] = data["middle"] + sigma * series.rolling(window=window).std()
        data["lower"] = data["middle"] - sigma * series.rolling(window=window).std()
        return data

    def generate_signal(self, series: pd.Series, window=None, sigma=None, loud=False):
        """
        Buy when crosses lower, sell when crosses higher
        """
        if not window or not sigma:
            window = self.window
            sigma = self.sigma
        bands = self.create_bands(series, window, sigma)

        now = bands.iloc[-1]
        last = bands.iloc[-2]
        signal = "hold"
        if now[series.name] < now.lower and last[series.name] > last.lower:
            signal = "buy"
        elif now[series.name] > now.upper and last[series.name] < last.upper:
            signal = "sell"
        if loud:
            print(f"Bowl: SIGNAL={signal} (window={self.window}, sigma={self.sigma})")
        return signal

    def backtest(
        self, series=pd.Series, window=None, sigma=None, desc=None, loud=False
    ):
        """
        Given data, create a dataframe w columns [price, signal, net]
        """
        # default
        if not window or not sigma:
            window = self.window
            sigma = self.sigma
        # init
        tested = pd.DataFrame(series)
        tested["signal"] = "hold"
        tested["net"] = 0

        starting_price = tested.iloc[0][series.name]
        final_price = tested.iloc[-1][series.name]

        # starting portfolio
        starting_portfolio = {"money": starting_price, "shares": 0}

        # updated portfolio
        current_portfolio = starting_portfolio.copy()

        for i in trange(self.window, tested.shape[0], leave=False, desc=desc):
            # get signals
            sliced = tested.iloc[:i][series.name]
            current_price = tested.iloc[i][series.name]
            sig = self.generate_signal(sliced, window, sigma)

            # do trades
            if sig == "buy" and current_portfolio["money"] >= current_price:
                current_portfolio["shares"] += 1
                current_portfolio["money"] -= current_price
            elif sig == "sell" and current_portfolio["shares"] >= 1:
                current_portfolio["shares"] -= 1
                current_portfolio["money"] += current_price
            else:  # reset to action taken
                sig = "hold"

            # calculate net
            net = (
                (
                    current_portfolio["shares"] * current_price
                    + current_portfolio["money"]
                )
                - (
                    starting_portfolio["shares"] * current_price
                    + starting_portfolio["money"]
                )
            ) / (
                starting_portfolio["shares"] * current_price
                + starting_portfolio["money"]
            )

            # set df
            tested.iloc[i, tested.columns.get_loc("signal")] = sig
            tested.iloc[i, tested.columns.get_loc("net")] = net
        buyandhold = ((final_price - starting_price) / starting_price) * 100
        num_trades = tested[tested["signal"] != "hold"].shape[0]
        if loud:
            print(
                f"Net: {tested.iloc[-1]['net']*100:.2f}% (window={window}, sigma={sigma}) (b&h: {buyandhold:.2f}%) (# of trades: {num_trades})"
            )
        return tested

    def optimize(
        self,
        series=pd.Series,
        window_range=np.arange(5, 23, 2),
        sigma_range=np.arange(1.65, 2, 0.01),
        loud=True,
    ):
        """
        Find the best params and set to
        """
        already_done = []
        best = -1e10
        bestparams = (-1, -1)
        print("Optimizing....")
        for i in window_range:
            for j in sigma_range:
                if i != j and (i, j) not in already_done:
                    j = round(j, 2)  # round to fix floating point opps
                    tested = self.backtest(
                        series, window=i, sigma=j, desc=f"({i}, {j})"
                    )
                    buyandhold = (
                        (tested.iloc[-1][series.name] - tested.iloc[0][series.name])
                        / tested.iloc[0][series.name]
                    ) * 100

                    if tested.iloc[-1]["net"] > best:
                        best = tested.iloc[-1]["net"]
                        bestparams = (i, j)
                        if loud:
                            print(
                                f"best: {best*100:.2f}%, best params: {bestparams} (b&h: {buyandhold:.2f}%)"
                            )
                    already_done.append((i, j))
        self.window = bestparams[0]
        self.sigma = bestparams[1]
        print(f"--\nbest: {best*100:.2f}%, best params: {bestparams}")

    def scipy_opt(
        self,
        series=pd.Series,
        window_range=np.arange(5, 23, 2),
        sigma_range=np.arange(1.6, 2, 0.02),
    ):
        pass

    def plot(self, data: pd.DataFrame):
        # declare figure
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["middle"],
                line=dict(color="blue", width=0.7),
                name="middle",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["upper"],
                line=dict(color="red", width=1.5),
                name="upper (Sell)",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["lower"],
                line=dict(color="green", width=1.5),
                name="Lower Band (Buy)",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["close"],
                line=dict(color="black", width=1.5),
                name="close",
            )
        )

        # Add titles
        fig.update_layout(
            title="SPY live share price evolution",
            yaxis_title="Stock Price (USD per Shares)",
        )

        # X-Axes
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=15, label="15m", step="minute", stepmode="backward"),
                        dict(count=45, label="45m", step="minute", stepmode="backward"),
                        dict(count=1, label="HTD", step="hour", stepmode="todate"),
                        dict(count=3, label="3h", step="hour", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
        )

        # Show
        fig.show()
