import argparse
import tempfile
import unittest
from pathlib import Path

import pytest

from stock_alert.main import parse_args


class TestParseArgs(unittest.TestCase):
    """
    A test suite for the `parse_args` function.
    """

    def test_empty_argument_list(self) -> None:
        """
        Tests that the function raises an error, when the required args are not given.
        """
        args = []
        with pytest.raises(SystemExit):
            parse_args(args)

    def test_valid_file_path(self) -> None:
        """
        Tests that the function returns a namespace object with `path_stock_list` set to the correct value when given a
        valid file path.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = tmp_dir + "/stocks.txt"
            file_path = Path(file_path)
            file_path.touch()
            args = ["--path-stock-list", file_path.as_posix()]
            result = parse_args(args)
            self.assertIsInstance(result, argparse.Namespace)
            self.assertEqual(result.path_stock_list, file_path.as_posix())

    def test_invalid_file_path(self) -> None:
        """
        Tests that the function raises a `FileNotFoundError` exception when a non-existent file path is given.
        """
        args = ["--path-stock-list", "non-existent-file.txt"]
        with self.assertRaises(FileNotFoundError):
            parse_args(args)

    def test_invalid_option(self) -> None:
        """
        Tests that the function raises an `ArgumentError` exception when an invalid option is given.
        """
        args = ["--path-stock-list", "non-existent-file.txt", "--invalid-option", "invalid-value"]
        with self.assertRaises(argparse.ArgumentError):
            parse_args(args)
