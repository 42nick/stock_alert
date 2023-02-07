import time
from lib2to3.pytree import Base
from os import P_NOWAIT
from pathlib import Path

import tqdm
import yfinance

from stock_alert.quickstart import send_mail
from stock_alert.util import get_stock_ticker


class BaseAlert:
    def __init__(self) -> None:
        self.info = ""

    def need_alert(self, ticker: yfinance.Ticker) -> bool:
        raise NotImplementedError


class NoAlert(BaseAlert):
    def __init__(self) -> None:
        super().__init__()

    def need_alert(self, ticker: yfinance.Ticker) -> bool:
        return False


class AlertRelativeDailyChange(BaseAlert):
    def __init__(self, rel_change_in_percent: float) -> None:
        super().__init__()
        self.rel_change_in_percent = rel_change_in_percent

        self.lower_bound = 1 - self.rel_change_in_percent
        self.upper_bound = 1 + self.rel_change_in_percent

        self.info = ""

    def need_alert(self, ticker: yfinance.Ticker) -> bool:
        df = ticker.history(period="1d", interval="5m")

        if df.empty:
            print(f"Empty dataframe for {ticker.ticker}")
            return False

        opening_price = df.iloc[0]["Open"]

        relative_change = df.iloc[-1]["Close"] / opening_price

        if relative_change < self.lower_bound:
            self.info = f"Stock price has decreased by {100 * (1 - relative_change):.2f} %"
        elif relative_change > self.upper_bound:
            self.info = f"Stock price has increased by {100 * (relative_change - 1):.2f} %"
        else:
            return False

        return True


class AbsolutHigherThan(BaseAlert):
    def __init__(self, threshold: float) -> None:
        super().__init__()
        self.threshold = threshold
        self.info = ""

    def need_alert(self, ticker: yfinance.Ticker) -> bool:
        if ticker.history(period="1d", interval="5m").iloc[-1]["Close"] > self.threshold:
            self.info = f"Stock price is higher than {self.threshold}"
            return True
        return False


class AbsolutLowerThan(BaseAlert):
    def __init__(self, threshold: float) -> None:
        super().__init__()
        self.threshold = threshold
        self.info = ""

    def need_alert(self, ticker: yfinance.Ticker) -> bool:
        if ticker.history(period="1d", interval="5m").iloc[-1]["Close"] < self.threshold:
            self.info = f"Stock price is lower than {self.threshold}"
            return True
        return False


class StockAlert:
    def __init__(self, path_to_csv: Path, receiver_mail: str = "") -> None:
        self.receiver_mail = receiver_mail

        # ------------ loading the stocks and gathering info from the web ------------ #

        # read the stock list from a file
        self.stock_list = self.read_stock_list(path_to_csv)

        # get the stock symbols via yahoo finance
        self.stock_symbols = self.get_stock_symbols(self.stock_list)

        # storing the stock tickers from yahoo finance
        self.stock_tickers = self.get_stock_tickers(self.stock_symbols)

        # getting the opening price of the stock of today via yahoo finance
        # self.opening_prices = self.get_opening_prices()  # TODO not needed currently

        # ggf. checking cyclically if the stock price has reached a certain threshold

        # setting up the alerts
        self.alerts: dict[str, BaseAlert] = {symbol: NoAlert() for symbol in self.stock_symbols}

    def spin(self, interval: float = 60) -> None:
        """
        This function checks cyclically for all given stocks whether their alert is raised.
        """
        while True:
            alert_triggered = False
            for idx, (symbol, ticker) in enumerate(zip(self.stock_symbols, self.stock_tickers)):
                if self.alerts[symbol].need_alert(ticker):
                    print(f"Alert for {self.stock_list[idx]}: {self.alerts[symbol].info}")
                    alert_triggered = True

                    if self.receiver_mail:
                        send_mail(
                            receiver_email=self.receiver_mail,
                            message_content=self.alerts[symbol].info,
                            subject=self.stock_list[idx],
                        )
            if not alert_triggered:
                print(f"nothing to report, sleeping for {interval} seconds")

            pbar = tqdm.tqdm(range(200), colour="green", bar_format="{l_bar}{bar:50}|")
            for _ in pbar:
                pbar.set_description(f"Waiting for {interval} seconds")
                time.sleep(interval / 200)
            alert_triggered = False

    def configure_alert(self, symbol: str, alert: BaseAlert) -> None:
        self.alerts[symbol] = alert

    def configure_same_alert_for_all(self, alert: BaseAlert) -> None:
        for symbol in self.stock_symbols:
            self.configure_alert(symbol, alert)

    @staticmethod
    def read_stock_list(path: Path) -> list[str]:
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

        pbar = tqdm.tqdm(stock_list, colour="green")

        # showing a progress bar with the stock symbols with a fixed string size
        for stock in pbar:
            pbar.set_description(f"Getting stock symbol for {stock}".ljust(50))
            symbol = get_stock_ticker(stock)
            stock_symbols.append(get_stock_ticker(stock)) if symbol else None
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
