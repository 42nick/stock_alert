import time
from lib2to3.pytree import Base
from pathlib import Path

import yfinance

from stock_alert.util import get_stock_ticker


class BaseAlert:
    def __init__(self) -> None:
        pass

    def need_alert(self, ticker: yfinance.Ticker):
        raise NotImplementedError


class NoAlert(BaseAlert):
    def __init__(self) -> None:
        super().__init__()

    def need_alert(self, ticker: yfinance.Ticker):
        return False


class AlertRelativeDailyChange(BaseAlert):
    def __init__(self, rel_change_in_percent: float) -> None:
        super().__init__()
        self.rel_change_in_percent = rel_change_in_percent

        self.lower_bound = 1 - self.rel_change_in_percent
        self.upper_bound = 1 + self.rel_change_in_percent

        self.info = ""

    def need_alert(self, ticker: yfinance.Ticker):
        df = ticker.history(period="1d", interval="5m")
        opening_price = df.iloc[0]["Open"]

        relative_change = df.iloc[-1]["Close"] / opening_price

        if relative_change < self.lower_bound:
            self.info = f"Stock price has decreased by {100 * (1 - relative_change):.2f} %"
        elif relative_change > self.upper_bound:
            self.info = f"Stock price has increased by {100 * (relative_change - 1):.2f} %"
        else:
            return False

        return True


class StockAlert:
    def __init__(self, path_to_csv: Path) -> None:

        # ------------ loading the stocks and gathering info from the web ------------ #

        # read the stock list from a file
        self.stock_list = self.read_stock_list(path_to_csv)

        # get the stock symbols via yahoo finance
        self.stock_symbols = self.get_stock_symbols(self.stock_list)

        # storing the stock tickers from yahoo finance
        self.stock_tickers = self.get_stock_tickers(self.stock_symbols)

        # getting the opening price of the stock of today via yahoo finance
        self.opening_prices = self.get_opening_prices()

        # ggf. checking cyclically if the stock price has reached a certain threshold

        # setting up the alerts
        self.alerts = {symbol: NoAlert() for symbol in self.stock_symbols}

    def spin(self, interval: float) -> None:
        """
        This function checks cyclically if the stock price has reached a certain threshold.
        """
        while True:
            alert_triggered = False
            for symbol, ticker in zip(self.stock_symbols, self.stock_tickers):
                if self.alerts[symbol].need_alert(ticker):
                    print(f"Alert for {symbol}: {self.alerts[symbol].info}")
                    alert_triggered = True

            if not alert_triggered:
                print(f"nothing to report, sleeping for {interval} seconds")
            time.sleep(interval)
            alert_triggered = False

    def configure_alert(self, symbol: str, alert: BaseAlert) -> None:
        self.alerts[symbol] = alert

    @staticmethod
    def read_stock_list(path: str) -> list[str]:
        """
        Read the stock list from a file.
        """
        with open(path, "r") as f:
            stock_list = f.read().splitlines()

        return stock_list

    @staticmethod
    def get_stock_symbols(stock_list: list[str]) -> list[str]:
        """
        Get the stock symbols via the yahoo finance.
        """
        stock_symbols = []
        for stock in stock_list:
            stock_symbols.append(get_stock_ticker(stock))
        return stock_symbols

    @staticmethod
    def get_stock_tickers(stock_symbols: list[str]) -> list[yfinance.Ticker]:
        """
        Get the stock tickers via the yahoo finance.
        """
        return [yfinance.Ticker(symbol) for symbol in stock_symbols]

    def get_opening_prices(self) -> list[float]:
        """
        Get the opening prices of the stocks of today via yahoo finance.
        """
        return [ticker.history(period="1d", interval="5m").iloc[0]["Open"] for ticker in self.stock_tickers]
