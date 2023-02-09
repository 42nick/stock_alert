import argparse
import sys
from pathlib import Path

from stock_alert.class_stock_alert import AlertRelativeDailyChange, StockAlert


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

    alert = StockAlert(Path(args.path_stock_list), receiver_mail="", remind_interval_h=1 / 70)
    # alert = StockAlert(Path(args.path_stock_list), receiver_mail=os.environ["TEST_MAIL"], remind_interval_h=1 / 70)
    alert.configure_same_alert_for_all(AlertRelativeDailyChange(0.03))
    alert.spin(30)


if __name__ == "__main__":
    main()
