import argparse
import sys

import pandas as pd
import yfinance as yf

from stock_alert.class_stock_alert import StockAlert
from stock_alert.util import get_stock_ticker


def read_stock_list(path: str) -> list[str]:
    """
    Read the stock list from a file.
    """
    with open(path, "r") as f:
        stock_list = f.read().splitlines()

    return stock_list


def get_stock_symbols(stock_list: list[str]) -> list[str]:
    """
    Get the stock symbols via the yahoo finance.
    """
    stock_symbols = []
    for stock in stock_list:
        stock_symbols.append(get_stock_ticker(stock))
    return stock_symbols


def get_yfinance_info(symbol: str) -> pd.DataFrame:
    stock_info = yf.Ticker(symbol)
    df = stock_info.history(period="1d", interval="5m")
    return df


def get_stock_opening_price(symbol: str) -> float:
    df = get_yfinance_info(symbol)
    opening_price = df.iloc[0]["Open"]
    return opening_price


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path-stock-list", help="Path to the file containing a .txt file the stocks of to watch", type=str
    )
    return parser.parse_args(args)


def main() -> None:
    """
    The core function of this awesome project.
    """
    args = parse_args(sys.argv[1:])
    print(args)

    # stock_list = read_stock_list(args.path_stock_list)
    # symbols = get_stock_symbols(stock_list)

    alert = StockAlert(args.path_stock_list)
    print(alert.opening_prices)


if __name__ == "__main__":
    main()
