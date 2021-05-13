from cycle import Cycler

import logging

logging.basicConfig(
    format="[%(name)s] %(levelname)s %(asctime)s %(message)s", level=logging.INFO
)
ticker = "tsla"  # ticker to care about

if __name__ == "__main__":
    c = Cycler()
    c.cycle("tsla")
