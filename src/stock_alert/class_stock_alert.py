import time
from lib2to3.pytree import Base
from os import P_NOWAIT
from pathlib import Path

import tqdm
import yfinance
from stock_alert.alerts import BaseAlert, NoAlert

from stock_alert.quickstart import send_mail
from stock_alert.util import get_stock_ticker, hours_to_seconds


class ReminderHandler:
    def __init__(self, remind_interval_h: float) -> None:
        self.remind_interval_s = hours_to_seconds(remind_interval_h)
        self.last_reminder = time.time() - self.remind_interval_s

    def need_reminder(self) -> bool:
        if time.time() - self.last_reminder > self.remind_interval_s:
            self.last_reminder = time.time()
            return True
        return False


class StockAlert:
    stock_symbol_mapping_filename = "stock_symbol_mapping.csv"

    def __init__(self, path_to_csv: Path, receiver_mail: str = "", remind_interval_h: float = 24) -> None:
        self.receiver_mail = receiver_mail
        self.remind_interval_h = remind_interval_h

        # ------------ loading the stocks and gathering info from the web ------------ #

        # read the stock list from a file
        stock_list = self.read_stock_list(path_to_csv)

        # if the stock symbol mapping file exists, load it and check for missing stocks
        stock_symbol_mapping_filepath = Path(
            path_to_csv.as_posix().replace(path_to_csv.name, StockAlert.stock_symbol_mapping_filename)
        )
        symbols = []
        if stock_symbol_mapping_filepath.exists():
            with open(stock_symbol_mapping_filepath, "r") as file:
                symbols = []
                for idx, line in enumerate(file.read().splitlines()):
                    stock, symbol = line.split(",")
                    if stock != stock_list[idx]:
                        print("Order of stocks in csv file has changed. Recreating the symbol mapping file.")
                        stock_symbol_mapping_filepath.unlink()
                        break
                    symbols.append(symbol)
            if symbols:
                print("Loaded stock symbol mapping file.")

        # get the stock symbols via yahoo finance
        stock_symbols = self.get_stock_symbols(stock_list) if not symbols else symbols

        # store symbols in csv for faster loading
        with open(str(path_to_csv).replace(path_to_csv.name, StockAlert.stock_symbol_mapping_filename), "w") as file:
            for stock, symbol in zip(stock_list, stock_symbols):
                file.write(f"{stock},{symbol}\n")

        # storing the stock tickers from yahoo finance
        self.stock_tickers = self.get_stock_tickers(stock_symbols)

        # setting up the alerts
        self.alerts: dict[str, BaseAlert] = {symbol: NoAlert() for symbol in stock_symbols}
        self.remind_handlers: dict[str, ReminderHandler] = {
            symbol: ReminderHandler(self.remind_interval_h) for symbol in stock_symbols
        }

    def spin(self, interval: float = 60) -> None:
        """
        This function checks cyclically for all given stocks whether their alert is raised.
        """
        while True:
            alert_triggered = False
            for idx, (symbol, ticker) in enumerate(self.stock_tickers.items()):
                if self.alerts[symbol].need_alert(ticker) and self.remind_handlers[symbol].need_reminder():
                    try:
                        if "longName" not in ticker.info:
                            stock_name = symbol
                        else:
                            stock_name = ticker.info["longName"]
                    except Exception as e:
                        print(f"Error while getting stock name for {symbol}: {e}")
                        stock_name = symbol
                    print(f"Alert for {stock_name:<40}: {self.alerts[symbol].info}")
                    alert_triggered = True
                    if self.receiver_mail:
                        send_mail(
                            receiver_email=self.receiver_mail,
                            message_content=self.alerts[symbol].info,
                            subject=stock_name,
                        )
            if not alert_triggered:
                print(f"nothing to report, sleeping for {interval} seconds")

            pbar = tqdm.tqdm(range(200), colour="green", bar_format="{l_bar}{bar:50}|")
            for _ in pbar:
                pbar.set_description(f"Waiting for {interval} seconds")
                time.sleep(interval / 200)

    def configure_alert(self, symbol: str, alert: BaseAlert) -> None:
        self.alerts[symbol] = alert

    def configure_same_alert_for_all(self, alert: BaseAlert) -> None:
        for symbol in self.stock_tickers.keys():
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
            stock_symbols.append(get_stock_ticker(stock) if symbol else "N/A")
        return stock_symbols

    @staticmethod
    def get_stock_tickers(stock_symbols: list[str]) -> dict[str, yfinance.Ticker]:
        """
        Get the stock tickers via the yahoo finance.
        """
        return {symbol: yfinance.Ticker(symbol) for symbol in stock_symbols if symbol != "N/A"}

    def get_opening_prices(self) -> list[float]:
        """
        Get the opening prices of the stocks of today via yahoo finance.
        """
        return [ticker.history(period="1d", interval="5m").iloc[0]["Open"] for ticker in self.stock_tickers]
