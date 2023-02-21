import unittest
from unittest.mock import MagicMock, Mock, patch

import yfinance

from stock_alert.alerts import AlertRelativeDailyChange, BaseAlert, NoAlert


class TestBaseAlert(unittest.TestCase):
    @patch("yfinance.Ticker")
    def test_init(self, mock_ticker):
        alert = BaseAlert()
        self.assertEqual(alert.info, "")
        mock_ticker.assert_not_called()

    @patch("yfinance.Ticker")
    def test_need_alert_raises_error(self, mock_ticker):
        alert = BaseAlert()
        mock_ticker.return_value = MagicMock()
        with self.assertRaises(NotImplementedError):
            alert.need_alert(mock_ticker.return_value)


class TestNoAlert(unittest.TestCase):
    @patch("yfinance.Ticker")
    def test_init(self, mock_ticker):
        alert = NoAlert()
        self.assertEqual(alert.info, "")
        mock_ticker.assert_not_called()

    @patch("yfinance.Ticker")
    def test_need_alert_returns_false(self, mock_ticker):
        alert = NoAlert()
        mock_ticker.return_value = MagicMock()
        self.assertFalse(alert.need_alert(mock_ticker.return_value))


class TestAlertRelativeDailyChange(unittest.TestCase):
    def test_need_alert_below_lower_bound(self):
        # Create a MagicMock object for Ticker
        ticker_mock = MagicMock(spec=yfinance.Ticker)
        # Create a mock Ticker object that returns a DataFrame with an opening price of 100 and a closing price of 95
        mock_df = Mock()
        mock_df.iloc = [{"Open": 100, "Close": 95}]
        mock_df.empty = False
        ticker_mock.history.return_value = mock_df
        ticker_mock.fast_info = {"currency": "USD"}

        # Instantiate an AlertRelativeDailyChange object with a lower bound of 0.02
        alert = AlertRelativeDailyChange(0.02)

        # Check that need_alert returns True and sets alert.info correctly
        self.assertTrue(alert.need_alert(ticker_mock))
        self.assertEqual(alert.info, "Stock price has decreased by 5.00 % falling from 100.00 to 95.00 USD.")

    def test_need_alert_above_upper_bound(self):
        # Create a MagicMock object for Ticker
        ticker_mock = MagicMock(spec=yfinance.Ticker)
        # Create a mock Ticker object that returns a DataFrame with an opening price of 100 and a closing price of 105
        mock_df = Mock()
        mock_df.iloc = [{"Open": 100, "Close": 105}]
        mock_df.empty = False
        ticker_mock.history.return_value = mock_df
        ticker_mock.fast_info = {"currency": "USD"}

        # Instantiate an AlertRelativeDailyChange object with an upper bound of 0.02
        alert = AlertRelativeDailyChange(0.02)

        # Check that need_alert returns True and sets alert.info correctly
        self.assertTrue(alert.need_alert(ticker_mock))
        self.assertEqual(alert.info, "Stock price has increased by 5.00 % rising from 100.00 to 105.00 USD.")

    def test_need_alert_within_bounds(self):
        # Create a MagicMock object for Ticker
        ticker_mock = MagicMock(spec=yfinance.Ticker)

        # Create a mock Ticker object that returns a DataFrame with an opening price of 100 and a closing price of 102
        mock_df = Mock()
        mock_df.iloc = [{"Open": 100, "Close": 102}]
        mock_df.empty = False
        ticker_mock.history.return_value = mock_df

        # Instantiate an AlertRelativeDailyChange object with a lower and upper bound of 0.02
        alert = AlertRelativeDailyChange(0.02)

        # Check that need_alert returns False
        self.assertFalse(alert.need_alert(ticker_mock))
