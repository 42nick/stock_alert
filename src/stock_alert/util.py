from typing import Any
import json
import urllib.request


def get_json_stock_info(raw_stock_name: str) -> dict[str, Any]:
    """
    Get the stock information from the yahoo finance.
    """

    url_encoded_stock_name = urllib.parse.quote(raw_stock_name)

    response = urllib.request.urlopen(f"https://query2.finance.yahoo.com/v1/finance/search?q={url_encoded_stock_name}")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    return data


def get_stock_ticker(raw_stock_name: str) -> str:
    """
    Get the stock ticker from the yahoo finance.
    """

    data = get_json_stock_info(raw_stock_name)
    if len(data["quotes"]) == 0:
        print(f"Could not find stock {raw_stock_name} on yahoo finance.")
        return ""
    stock_ticker = data["quotes"][0]["symbol"]
    return stock_ticker
