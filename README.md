# strike

Strike is an algorithmic trading platform centered around bollinger bands.

## Workflow

Workflow is pretty simple. Here's a quick example using the alpaca trade api.

```python

import alpaca_trade_api as alpaca

alpaca = REST(
    key_id=api_key, secret_key=api_secret, base_url=base_url, api_version="v2"
)

df = alpaca.get_bars(
    ticker,
    TimeFrame.Minute,
    (datetime.now() - timedelta(hours=24 * days)).strftime(DTFORMAT),
    datetime.now().strftime(DTFORMAT),
    adjustment="raw",
).df

bowler = Bowl()

bowler.optimize(df["close"])
bowler.backtest(df["close"], loud=True)
```

`optimize` grid-searches the parameters for the best combination. This sets the controlling values for the best result. Then, it calls `backtest` to test on the previous data. 
