"""scanner 扫描逻辑测试。"""

import pandas as pd
import pytest

from src.output.signals import Signal, AttributedSignal, ScanResult


def _make_daily_data() -> pd.DataFrame:
    dates = pd.bdate_range("2023-01-01", periods=30)
    prices = [100.0]
    for i in range(29):
        if i == 10:
            prices.append(prices[-1] * 1.10)   # +10%
        elif i == 20:
            prices.append(prices[-1] * 0.88)   # -12%
        else:
            prices.append(prices[-1] * (1 + 0.005 * ((-1) ** i)))
    return pd.DataFrame({
        "Date": dates,
        "Open": [p * 0.99 for p in prices],
        "Close": prices,
        "Adj Close": prices,
        "Volume": [1_000_000] * 30,
    })


class TestScannerLogic:
    def test_find_triggered_events(self):
        df = _make_daily_data()
        df["daily_return"] = df["Adj Close"].pct_change() * 100
        threshold = 8.0

        triggered = df[df["daily_return"].abs() >= threshold].dropna(subset=["daily_return"])
        assert len(triggered) == 2

    def test_signal_creation(self):
        sig = Signal(
            ticker="TEST",
            company_name="Test Corp",
            sector="Technology",
            event_date="2023-01-15",
            daily_return_pct=-10.5,
            volume_change_pct=200.0,
            price_before=100.0,
            price_after=89.5,
        )
        assert sig.ticker == "TEST"
        assert sig.daily_return_pct == -10.5

    def test_volume_change_calculation(self):
        volumes = [1_000_000] * 20 + [3_000_000]
        ma20 = sum(volumes[:20]) / 20
        vol_change = ((volumes[20] - ma20) / ma20) * 100
        assert vol_change == 200.0

    def test_scan_result_serialization(self, tmp_path):
        signals = [
            AttributedSignal(
                ticker="AAPL", company_name="Apple", sector="Tech",
                event_date="2023-06-01", daily_return_pct=-8.0,
                volume_change_pct=150.0, price_before=180.0, price_after=165.6,
            ),
        ]
        result = ScanResult(
            market="us", threshold_pct=7.0, scan_date="2023-12-01",
            total_scanned=500, total_triggered=1, signals=signals,
        )
        path = tmp_path / "test_scan.json"
        result.save(path)
        loaded = ScanResult.load(path)

        assert loaded.total_scanned == 500
        assert len(loaded.signals) == 1
        assert loaded.signals[0].ticker == "AAPL"
