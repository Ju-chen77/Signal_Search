"""benchmark 计算逻辑测试。"""

import numpy as np
import pandas as pd
import pytest

from src.output.signals import BenchmarkEvent, BenchmarkResult


def _make_price_df(prices: list[float]) -> pd.DataFrame:
    """构造一个简单的 DataFrame 用于测试。"""
    dates = pd.bdate_range("2020-01-01", periods=len(prices))
    return pd.DataFrame({
        "Date": dates,
        "Open": prices,
        "High": [p * 1.01 for p in prices],
        "Low": [p * 0.99 for p in prices],
        "Close": prices,
        "Adj Close": prices,
        "Volume": [1_000_000] * len(prices),
    })


class TestBenchmarkLogic:
    def test_daily_returns(self):
        prices = [100, 110, 105, 115, 100]
        df = _make_price_df(prices)
        returns = df["Adj Close"].pct_change() * 100
        returns = returns.dropna()

        assert len(returns) == 4
        assert round(returns.iloc[0], 1) == 10.0   # 100 -> 110
        assert round(returns.iloc[1], 1) == -4.5    # 110 -> 105

    def test_percentile_threshold(self):
        np.random.seed(42)
        normal = np.random.normal(0, 1, 1000)
        normal = np.append(normal, [10, -12, 8, -9, 15])

        p99 = np.percentile(np.abs(normal), 99)
        assert p99 > 2.0

        significant = normal[np.abs(normal) >= p99]
        assert len(significant) > 0

        min_significant = min(np.abs(significant))
        assert min_significant >= p99

    def test_benchmark_result_serialization(self, tmp_path):
        events = [
            BenchmarkEvent("AAPL", "Apple", "2023-01-15", -7.5, 150.0, 5000000),
            BenchmarkEvent("TSLA", "Tesla", "2023-03-20", 12.3, 200.0, 8000000),
        ]
        result = BenchmarkResult(
            market="us",
            threshold_pct=7.5,
            benchmark_events=events,
            metadata={"lookback_years": 5, "percentile": 99},
        )

        path = tmp_path / "test_bm.json"
        result.save(path)
        loaded = BenchmarkResult.load(path)

        assert loaded.market == "us"
        assert loaded.threshold_pct == 7.5
        assert len(loaded.benchmark_events) == 2
        assert loaded.benchmark_events[0].ticker == "AAPL"

    def test_threshold_takes_minimum(self):
        events = [
            BenchmarkEvent("A", "A", "2023-01-01", -10.0, 100, 1000),
            BenchmarkEvent("B", "B", "2023-01-02", 7.5, 200, 2000),
            BenchmarkEvent("A", "A", "2023-01-03", 15.0, 110, 1500),
        ]

        min_abs = min(abs(e.daily_return_pct) for e in events)
        assert min_abs == 7.5
