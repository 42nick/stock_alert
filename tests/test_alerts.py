import unittest
from unittest.mock import MagicMock, Mock, patch

import yfinance

from stock_alert.alerts import AbsolutHigherThan, AbsolutLowerThan, AlertRelativeDailyChange, BaseAlert, NoAlert


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

        # mimic the case where the ticker is not available
        mock_df.empty = True
        ticker_mock.ticker = "TEST"
        self.assertFalse(alert.need_alert(ticker_mock))


class TestAbsolutHigherThan(unittest.TestCase):
    def test_need_alert_true(self):
        """Test that need_alert returns True when the ticker price is higher than the threshold."""
        threshold = 100
        ticker_mock = MagicMock()
        mock_df = Mock()
        mock_df.iloc = [{"Close": 102}]
        ticker_mock.history.return_value = mock_df

        alert = AbsolutHigherThan(threshold)
        result = alert.need_alert(ticker_mock)

        self.assertTrue(result)
        self.assertEqual(alert.info, f"Stock price is higher than {threshold}")

    def test_need_alert_false(self):
        """Test that need_alert returns False when the ticker price is lower than the threshold."""
        threshold = 100
        ticker_mock = MagicMock()
        mock_df = Mock()
        mock_df.iloc = [{"Close": 90}]
        ticker_mock.history.return_value = mock_df
        alert = AbsolutHigherThan(threshold)
        result = alert.need_alert(ticker_mock)

        self.assertFalse(result)
        self.assertEqual(alert.info, "")


class TestAbsolutLowerThan(unittest.TestCase):
    def test_need_alert_true(self):
        """Test that need_alert returns True when the ticker price is higher than the threshold."""
        threshold = 100
        ticker_mock = MagicMock()
        mock_df = Mock()
        mock_df.iloc = [{"Close": 99}]
        ticker_mock.history.return_value = mock_df

        alert = AbsolutLowerThan(threshold)
        result = alert.need_alert(ticker_mock)

        self.assertTrue(result)
        self.assertEqual(alert.info, f"Stock price is lower than {threshold}")

    def test_need_alert_false(self):
        """Test that need_alert returns False when the ticker price is lower than the threshold."""
        threshold = 100
        ticker_mock = MagicMock()
        mock_df = Mock()
        mock_df.iloc = [{"Close": 120}]
        ticker_mock.history.return_value = mock_df
        alert = AbsolutLowerThan(threshold)
        result = alert.need_alert(ticker_mock)

        self.assertFalse(result)
        self.assertEqual(alert.info, "")
