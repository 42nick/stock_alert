import argparse
import sys
from pathlib import Path

from stock_alert.alerts import AlertRelativeDailyChange
from stock_alert.class_stock_alert import StockAlert


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path-stock-list",
        help="Path to the file containing a .txt file the stocks of to watch",
        type=str,
        required=True,
    )

    args, undesired = parser.parse_known_args(args)

    if undesired is not None and len(undesired) > 0:
        raise argparse.ArgumentError(None, f"Undesired arguments: {undesired}")

    if Path(args.path_stock_list).is_file() is False:
        raise FileNotFoundError(f"File {args.path_stock_list} does not exist")

    return args


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
