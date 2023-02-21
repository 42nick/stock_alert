import yfinance


class BaseAlert:
    def __init__(self) -> None:
        self.info = ""

    def need_alert(self, ticker: yfinance.Ticker) -> bool:
        raise NotImplementedError


class NoAlert(BaseAlert):
    def __init__(self) -> None:
        super().__init__()

    def need_alert(self, ticker: yfinance.Ticker) -> bool:
        return False


class AlertRelativeDailyChange(BaseAlert):
    def __init__(self, rel_change_in_percent: float) -> None:
        super().__init__()
        self.rel_change_in_percent = rel_change_in_percent

        self.lower_bound = 1 - self.rel_change_in_percent
        self.upper_bound = 1 + self.rel_change_in_percent

        self.info = ""

    def need_alert(self, ticker: yfinance.Ticker) -> bool:
        df = ticker.history(period="1d", interval="5m")

        if df.empty:
            print(f"Empty dataframe for {ticker.ticker}")
            return False

        opening_price = df.iloc[0]["Open"]
        closing_price = df.iloc[-1]["Close"]

        relative_change = closing_price / opening_price

        if relative_change < self.lower_bound:
            self.info = f"Stock price has decreased by {100 * (1 - relative_change):.2f} % falling from {opening_price:.2f} to {closing_price:.2f} {ticker.fast_info['currency']}."
        elif relative_change > self.upper_bound:
            self.info = f"Stock price has increased by {100 * (relative_change - 1):.2f} % rising from {opening_price:.2f} to {closing_price:.2f} {ticker.fast_info['currency']}."
        else:
            return False

        return True


class AbsolutHigherThan(BaseAlert):
    def __init__(self, threshold: float) -> None:
        super().__init__()
        self.threshold = threshold
        self.info = ""

    def need_alert(self, ticker: yfinance.Ticker) -> bool:
        if ticker.history(period="1d", interval="5m").iloc[-1]["Close"] > self.threshold:
            self.info = f"Stock price is higher than {self.threshold}"
            return True
        return False


class AbsolutLowerThan(BaseAlert):
    def __init__(self, threshold: float) -> None:
        super().__init__()
        self.threshold = threshold
        self.info = ""

    def need_alert(self, ticker: yfinance.Ticker) -> bool:
        if ticker.history(period="1d", interval="5m").iloc[-1]["Close"] < self.threshold:
            self.info = f"Stock price is lower than {self.threshold}"
            return True
        return False
