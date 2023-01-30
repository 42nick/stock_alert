from stock_alert.example_function import add_two_values


def test_add_two_values() -> None:
    assert add_two_values(2, 3) == 5
