# stock_alert
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Stock Alert is a Python package that allows you to set alerts on the price of stocks listed on Yahoo Finance. With Stock
Alert, you can create alert objects that will monitor the price of a particular stock and notify you via email when the
stock price meets certain conditions.

## Installation
```
git clone https://github.com/42nick/stock_alert.git
cd stock_alert
pip install .
```

## Usage
To use Stock Alert, you first need to create an alert object. There are several types of alerts that you can create:

* NoAlert: This alert object does not send any notifications and always returns False.
* AlertRelativeDailyChange: This alert object triggers a notification when the daily relative change of a stock price exceeds a certain percentage.
* AbsolutHigherThan: This alert object triggers a notification when the stock price exceeds a certain absolute value.
* Here's an example of how to create an alert object for a daily relative change of 5%:
```python
import yfinance as yf
from stock_alert import AlertRelativeDailyChange

ticker = yf.Ticker("AAPL")
alert = AlertRelativeDailyChange(5.0)
if alert.need_alert(ticker):
    # send notification
    print(alert.info)
```


## Todo
- [ ] Add tests
- [x] Add mail client who sends alerts to the user
- [ ] stock visualization, some dash app
- [x] store stock symbols 

## Building the docs
```
sphinx-build -b html docs/source docs/build
```

[Documentation](./docs/source/index.rst)

