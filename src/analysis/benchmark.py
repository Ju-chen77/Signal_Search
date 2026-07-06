"""从 benchmark 公司历史数据中计算波动率基准门槛。

核心逻辑：
1. 拉取每家 benchmark 公司过去 N 年日线数据
2. 计算日收益率（基于 Adj Close）
3. 对每家公司，取日收益率绝对值的第 99 百分位以上作为"显著波动"
4. 收集所有 benchmark 公司的显著波动事件
5. 取其中绝对值最小的作为市场基准门槛
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src.data.yahoo_client import get_stock_history, batch_download
from src.data.akshare_client import batch_download_hk
from src.output.signals import BenchmarkEvent, BenchmarkResult

_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "benchmarks.yaml"


def _load_market_config(market: str = "us") -> dict:
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg["markets"][market]


def _compute_daily_returns(df: pd.DataFrame) -> pd.Series:
    """用 Adj Close 计算日收益率百分比，过滤掉拆股/除权造成的假波动。"""
    col = "Adj Close" if "Adj Close" in df.columns else "Close"
    returns = df[col].pct_change() * 100
    return returns.dropna()


def calculate_benchmark(market: str = "us") -> BenchmarkResult:
    """计算指定市场的波动率基准。"""
    cfg = _load_market_config(market)
    benchmarks = cfg["benchmarks"]
    lookback = cfg.get("lookback_years", 5)
    percentile = cfg.get("percentile", 99)

    all_events: list[BenchmarkEvent] = []

    # 批量下载所有 benchmark 公司数据
    ticker_list = [bm["ticker"] for bm in benchmarks]
    name_map = {bm["ticker"]: bm["name"] for bm in benchmarks}
    print(f"[benchmark] 批量下载 {len(ticker_list)} 家公司数据 ...")
    if market == "hk":
        all_data = batch_download_hk(ticker_list, years=lookback)
    else:
        all_data = batch_download(ticker_list, years=lookback)

    for bm in benchmarks:
        ticker = bm["ticker"]
        name = bm["name"]
        print(f"[benchmark] 分析 {name} ({ticker}) ...")

        df = all_data.get(ticker, pd.DataFrame())
        if df.empty:
            print(f"[benchmark] {ticker} 无数据，跳过")
            continue

        returns = _compute_daily_returns(df)
        if returns.empty:
            continue

        threshold = np.percentile(returns.abs(), percentile)

        significant_mask = returns.abs() >= threshold
        significant_dates = df.loc[returns[significant_mask].index]

        for idx in returns[significant_mask].index:
            row = df.loc[idx]
            date_val = row.get("Date", "")
            if hasattr(date_val, "strftime"):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val)

            close_col = "Adj Close" if "Adj Close" in df.columns else "Close"
            all_events.append(BenchmarkEvent(
                ticker=ticker,
                company_name=name,
                date=date_str,
                daily_return_pct=round(float(returns.loc[idx]), 2),
                close_price=round(float(row[close_col]), 2),
                volume=int(row.get("Volume", 0)),
            ))

    if not all_events:
        print("[benchmark] 警告：没有找到任何显著波动事件")
        return BenchmarkResult(
            market=market,
            threshold_pct=0.0,
            benchmark_events=[],
            metadata={"lookback_years": lookback, "percentile": percentile},
        )

    abs_returns = sorted(abs(e.daily_return_pct) for e in all_events)
    median_abs = abs_returns[len(abs_returns) // 2]
    threshold_pct = round(median_abs, 2)

    print(f"[benchmark] 共 {len(all_events)} 个显著波动事件")
    print(f"[benchmark] 波动率门槛 = ±{threshold_pct}%（所有大波动的中位数）")

    return BenchmarkResult(
        market=market,
        threshold_pct=threshold_pct,
        benchmark_events=all_events,
        metadata={
            "lookback_years": lookback,
            "percentile": percentile,
            "num_benchmarks": len(benchmarks),
            "num_events": len(all_events),
        },
    )
