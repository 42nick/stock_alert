import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from stock_alert.class_stock_alert import StockAlert


def test_read_stock_list():
    # Create a temporary file with stock names
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("AAPL\nTSLA\nAMZN\n")
        temp_path = Path(f.name)

    # Mock the open function to return a MagicMock object
    open_mock = MagicMock()
    open_mock.return_value.__enter__.return_value.read.return_value = "AAPL\nTSLA\nAMZN\n"
    with patch("builtins.open", open_mock):
        # Test that the function returns the expected list of stock names
        assert StockAlert.read_stock_list(temp_path) == ["AAPL", "TSLA", "AMZN"]

    # Clean up the temporary file
    temp_path.unlink()
