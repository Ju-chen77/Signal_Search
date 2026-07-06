"""用 benchmark 基准扫描目标市场，找出触发争议波动信号的股票。

使用批量下载，50只一批，比逐只拉快10倍且不容易被限流。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

import yaml

from src.data.yahoo_client import get_sp500_tickers, get_hsi_tickers, batch_download, get_stock_history, get_stock_info
from src.data.akshare_client import batch_download_hk, get_hk_stock_info, download_sector_indices
from src.output.signals import BenchmarkResult, Signal, ScanResult, AttributedSignal

_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "benchmarks.yaml"


def _load_hk_sector_config() -> tuple[dict[str, str], dict[str, str]]:
    """从配置文件加载行业映射和行业指数映射。"""
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    hk = cfg["markets"]["hk"]
    sector_mapping: dict[str, str] = hk.get("sector_mapping", {})
    sector_indices: dict[str, str] = hk.get("sector_indices", {})
    return sector_mapping, sector_indices


def scan_market(market: str = "us", benchmark: BenchmarkResult | None = None) -> ScanResult:
    """扫描市场，找出日收益率超过门槛的所有事件。"""
    if benchmark is None:
        raise ValueError("必须先计算 benchmark 基准")

    threshold = benchmark.threshold_pct

    if market == "us":
        tickers = get_sp500_tickers()
    elif market == "hk":
        tickers = get_hsi_tickers()
    else:
        print(f"[scanner] {market} 市场扫描尚未实现 (v0.3)")
        return ScanResult(
            market=market,
            threshold_pct=threshold,
            scan_date=datetime.now().strftime("%Y-%m-%d"),
            total_scanned=0,
            total_triggered=0,
        )
    if not tickers:
        print("[scanner] 无法获取 S&P 500 列表")
        return ScanResult(
            market=market,
            threshold_pct=threshold,
            scan_date=datetime.now().strftime("%Y-%m-%d"),
            total_scanned=0,
            total_triggered=0,
        )

    total = len(tickers)
    market_label = "恒生指数" if market == "hk" else "S&P 500"
    print(f"[scanner] 开始扫描 {total} 只 {market_label} 股票，门槛 ±{threshold}%")

    print(f"[scanner] 正在批量下载股价数据 ...")
    if market == "hk":
        all_data = batch_download_hk(tickers, years=5)
    else:
        all_data = batch_download(tickers, years=5)

    all_signals: list[Signal] = []
    failed: list[str] = []

    sector_mapping: dict[str, str] = {}
    if market == "hk":
        sector_mapping, _ = _load_hk_sector_config()
        print(f"[scanner] 已加载 {len(sector_mapping)} 只股票的行业分类")

    print(f"[scanner] 开始分析 {len(all_data)} 只有数据的股票 ...")

    for i, ticker in enumerate(tickers, 1):
        if i % 100 == 0:
            print(f"[scanner] 分析进度 {i}/{total}")

        df = all_data.get(ticker)
        if df is None or df.empty or len(df) < 21:
            continue

        try:
            close_col = "Adj Close" if "Adj Close" in df.columns else "Close"
            df = df.copy()
            df["daily_return"] = df[close_col].pct_change() * 100
            df["vol_ma20"] = df["Volume"].rolling(20).mean()
            df["vol_change"] = ((df["Volume"] - df["vol_ma20"]) / df["vol_ma20"]) * 100

            triggered = df[df["daily_return"].abs() >= threshold].dropna(subset=["daily_return"])

            if triggered.empty:
                continue

            info = get_hk_stock_info(ticker) if market == "hk" else get_stock_info(ticker)
            sector = sector_mapping.get(ticker, info.get("sector", "Unknown"))

            for _, row in triggered.iterrows():
                date_val = row.get("Date", "")
                if hasattr(date_val, "strftime"):
                    date_str = date_val.strftime("%Y-%m-%d")
                else:
                    date_str = str(date_val)

                all_signals.append(Signal(
                    ticker=ticker,
                    company_name=info.get("name", ticker),
                    sector=sector,
                    event_date=date_str,
                    daily_return_pct=round(float(row["daily_return"]), 2),
                    volume_change_pct=round(float(row.get("vol_change", 0)), 2) if pd.notna(row.get("vol_change")) else 0.0,
                    price_before=round(float(row.get("Open", 0)), 2),
                    price_after=round(float(row.get(close_col, 0)), 2),
                ))
        except Exception as exc:
            failed.append(ticker)
            continue

    if market == "hk" and all_signals:
        _enrich_excess_returns(all_signals)
        _enrich_earnings_proximity(all_signals)

    all_signals.sort(key=lambda s: s.event_date, reverse=True)

    triggered_tickers = len(set(s.ticker for s in all_signals))
    company_specific = sum(1 for s in all_signals if s.is_company_specific)
    print(f"[scanner] 扫描完成：{total} 只股票，{triggered_tickers} 只触发信号，共 {len(all_signals)} 个事件")
    if market == "hk":
        print(f"[scanner] 其中 {company_specific} 个为公司特有事件，{len(all_signals) - company_specific} 个跟随大盘")
    if failed:
        print(f"[scanner] {len(failed)} 只分析失败")

    attributed = [AttributedSignal.from_signal(s) for s in all_signals]

    return ScanResult(
        market=market,
        threshold_pct=threshold,
        scan_date=datetime.now().strftime("%Y-%m-%d"),
        total_scanned=total,
        total_triggered=triggered_tickers,
        signals=attributed,
    )


def _enrich_excess_returns(signals: list[Signal]) -> None:
    """用行业指数计算每个事件的超额波动（科技对标HSTECH、银行对标HSMBI等）。"""
    _, sector_indices_cfg = _load_hk_sector_config()

    needed_indices = set()
    for sig in signals:
        idx = sector_indices_cfg.get(sig.sector, "HSI")
        needed_indices.add(idx)
    needed_indices.add("HSI")

    print(f"[scanner] 下载 {len(needed_indices)} 个行业指数: {', '.join(sorted(needed_indices))}")
    all_indices = download_sector_indices(years=5)

    index_maps: dict[str, dict[str, float]] = {}
    for symbol, df in all_indices.items():
        df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")
        index_maps[symbol] = dict(zip(df["date_str"], df["daily_return_pct"]))

    matched = 0
    sector_stats: dict[str, int] = {}
    for sig in signals:
        idx_symbol = sector_indices_cfg.get(sig.sector, "HSI")
        idx_map = index_maps.get(idx_symbol, index_maps.get("HSI", {}))

        mkt_ret = idx_map.get(sig.event_date, 0.0)
        if pd.notna(mkt_ret):
            sig.market_return_pct = round(float(mkt_ret), 2)
        else:
            sig.market_return_pct = 0.0
        sig.excess_return_pct = round(sig.daily_return_pct - sig.market_return_pct, 2)
        sig.is_company_specific = abs(sig.excess_return_pct) > abs(sig.market_return_pct)
        sig.sector_index = idx_symbol
        if sig.market_return_pct != 0.0:
            matched += 1
        sector_stats[idx_symbol] = sector_stats.get(idx_symbol, 0) + 1

    print(f"[scanner] {matched}/{len(signals)} 个事件匹配到行业指数数据")
    for idx, cnt in sorted(sector_stats.items(), key=lambda x: -x[1]):
        print(f"[scanner]   {idx}: {cnt} 个事件")


def _enrich_earnings_proximity(signals: list[Signal], days: int = 3) -> None:
    """用 yfinance 拉取每家公司的财报发布日期，标记±N天内的事件。"""
    import os
    import json
    import yfinance as yf

    cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / "prices" / "earnings"
    cache_dir.mkdir(parents=True, exist_ok=True)

    tickers = sorted(set(s.ticker for s in signals))
    print(f"[scanner] 拉取 {len(tickers)} 只股票的财报日期（yfinance）...")

    earnings_map: dict[str, list[datetime]] = {}
    fetched = 0
    failed = 0

    for i, ticker in enumerate(tickers, 1):
        if i % 10 == 1 or i == len(tickers):
            print(f"[scanner]   财报日期 {i}/{len(tickers)} (已获取 {fetched}, 失败 {failed})")

        cache_file = cache_dir / f"{ticker.replace('.', '_')}.json"
        if cache_file.exists():
            cached = json.loads(cache_file.read_text())
            if cached:
                earnings_map[ticker] = [datetime.strptime(d, "%Y-%m-%d") for d in cached]
                fetched += 1
            continue

        try:
            ed = yf.Ticker(ticker).earnings_dates
            if ed is not None and not ed.empty:
                dates = [d.to_pydatetime().replace(tzinfo=None) for d in ed.index]
                earnings_map[ticker] = dates
                cache_file.write_text(json.dumps([d.strftime("%Y-%m-%d") for d in dates]))
                fetched += 1
            else:
                cache_file.write_text("[]")
        except Exception as exc:
            failed += 1
            if i <= 3:
                print(f"[scanner]   {ticker} 财报日期获取失败: {exc}")
            cache_file.write_text("[]")

    print(f"[scanner] 财报日期：{fetched}/{len(tickers)} 成功, {failed} 失败")

    matched = 0
    for sig in signals:
        edates = earnings_map.get(sig.ticker, [])
        if not edates:
            continue
        event_dt = datetime.strptime(sig.event_date, "%Y-%m-%d")
        for ed in edates:
            diff = abs((event_dt - ed).days)
            if diff <= days:
                sig.near_earnings = True
                sig.earnings_date = ed.strftime("%Y-%m-%d")
                matched += 1
                break

    print(f"[scanner] {matched}/{len(signals)} 个事件在财报日±{days}天内")
