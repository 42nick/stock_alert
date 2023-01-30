import urllib.request
import json


def get_json_stock_info(raw_stock_name: str) -> dict:
    """
    Get the stock information from the yahoo finance.
    """

    response = urllib.request.urlopen(f"https://query2.finance.yahoo.com/v1/finance/search?q={raw_stock_name}")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    return data


def get_stock_ticker(raw_stock_name: str) -> str:
    """
    Get the stock ticker from the yahoo finance.
    """

    data = get_json_stock_info(raw_stock_name)
    stock_ticker = data["quotes"][0]["symbol"]
    return stock_ticker
