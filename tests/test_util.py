import json
from unittest import TestCase
from unittest.mock import MagicMock, patch

from stock_alert.util import get_json_stock_info, get_stock_ticker, hours_to_seconds


def test_hours_to_seconds():
    # Test a whole number of hours
    assert hours_to_seconds(1) == 3600

    # Test a fraction of an hour
    assert hours_to_seconds(0.5) == 1800

    # Test zero hours
    assert hours_to_seconds(0) == 0

    # Test negative hours
    assert hours_to_seconds(-1) == -3600


def test_get_json_stock_info():
    # Example raw stock name to test
    raw_stock_name = "AAPL"

    # Example JSON response to return when `urllib.request.urlopen` is called
    expected_json_response = {"quotes": [{"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NMS", "type": "Equity"}]}

    # Create a mock for `urllib.request.urlopen` using `MagicMock`
    mock_urlopen = MagicMock()()

    # Set the `read` method of the mock to return the expected JSON response
    mock_urlopen.return_value.read.return_value = json.dumps(expected_json_response).encode("utf8")

    # Patch `urllib.request.urlopen` with the mock
    with patch("urllib.request.urlopen", mock_urlopen):
        # Call the function with the example stock name
        result = get_json_stock_info(raw_stock_name)

        # Assert that the returned data matches the expected JSON response
        assert result == expected_json_response


class TestGetStockTicker(TestCase):
    def test_get_stock_ticker_returns_ticker_when_successful(self):
        """
        Test that get_stock_ticker returns a stock ticker when successful.
        """
        # Create a MagicMock object for the get_json_stock_info function
        get_json_stock_info_mock = MagicMock()
        # Set the return value for the get_json_stock_info function
        get_json_stock_info_mock.return_value = {"quotes": [{"symbol": "AAPL"}]}

        # Patch the get_json_stock_info function with the MagicMock object
        with patch("stock_alert.util.get_json_stock_info", get_json_stock_info_mock):
            # Call the get_stock_ticker function with a valid stock name
            stock_ticker = get_stock_ticker("Apple")
            # Assert that the stock ticker is the expected value
            self.assertEqual(stock_ticker, "AAPL")

        # Assert that the get_json_stock_info function was called once with the correct argument
        get_json_stock_info_mock.assert_called_once_with("Apple")

    def test_get_stock_ticker_returns_empty_string_when_unsuccessful(self):
        """
        Test that get_stock_ticker returns an empty string when unsuccessful.
        """
        # Create a MagicMock object for the get_json_stock_info function
        get_json_stock_info_mock = MagicMock()
        # Set the return value for the get_json_stock_info function
        get_json_stock_info_mock.return_value = {"quotes": []}

        # Patch the get_json_stock_info function with the MagicMock object
        with patch("stock_alert.util.get_json_stock_info", get_json_stock_info_mock):
            # Call the get_stock_ticker function with an invalid stock name
            stock_ticker = get_stock_ticker("Invalid Stock")
            # Assert that the stock ticker is an empty string
            self.assertEqual(stock_ticker, "")

        # Assert that the get_json_stock_info function was called once with the correct argument
        get_json_stock_info_mock.assert_called_once_with("Invalid Stock")
