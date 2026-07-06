"""FastAPI 后端，为前端提供信号数据。"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src.output.signals import BenchmarkResult, ScanResult

app = FastAPI(title="Controversy Signal Radar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "signals"


def _load_benchmark(market: str = "us") -> BenchmarkResult | None:
    path = _DATA_DIR / f"benchmark_{market}.json"
    if not path.exists():
        return None
    return BenchmarkResult.load(path)


def _load_scan(market: str = "us") -> ScanResult | None:
    path = _DATA_DIR / f"full_{market}.json"
    if not path.exists():
        path = _DATA_DIR / f"scan_{market}.json"
    if not path.exists():
        return None
    return ScanResult.load(path)


@app.get("/api/benchmark")
def get_benchmark(market: str = "us"):
    bm = _load_benchmark(market)
    if bm is None:
        return {"error": "Benchmark 数据不存在，请先运行 run_benchmark.py"}
    return asdict(bm)


@app.get("/api/signals")
def get_signals(
    market: str = "us",
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sort: str = Query("recent"),
    filter: str = Query("all"),
    sector: str = Query("all"),
):
    scan = _load_scan(market)
    if scan is None:
        return {"error": "扫描数据不存在，请先运行 run_full.py"}

    signals = scan.signals

    if filter == "company":
        signals = [s for s in signals if s.is_company_specific]
    elif filter == "market":
        signals = [s for s in signals if not s.is_company_specific]

    if sector != "all":
        signals = [s for s in signals if s.sector == sector]

    if sort == "magnitude":
        signals = sorted(signals, key=lambda s: abs(s.daily_return_pct), reverse=True)
    elif sort == "excess":
        signals = sorted(signals, key=lambda s: abs(s.excess_return_pct), reverse=True)
    elif sort == "frequency":
        ticker_count: dict[str, int] = {}
        for s in signals:
            ticker_count[s.ticker] = ticker_count.get(s.ticker, 0) + 1
        signals = sorted(signals, key=lambda s: ticker_count[s.ticker], reverse=True)
    else:
        signals = sorted(signals, key=lambda s: s.event_date, reverse=True)

    page = signals[offset : offset + limit]

    return {
        "market": scan.market,
        "threshold_pct": scan.threshold_pct,
        "scan_date": scan.scan_date,
        "total_scanned": scan.total_scanned,
        "total_triggered": scan.total_triggered,
        "total_events": len(signals),
        "signals": [asdict(s) for s in page],
    }


@app.get("/api/signals/{ticker}")
def get_ticker_signals(ticker: str, market: str = "us"):
    scan = _load_scan(market)
    if scan is None:
        return {"error": "扫描数据不存在"}

    events = [s for s in scan.signals if s.ticker.upper() == ticker.upper()]
    if not events:
        return {"error": f"未找到 {ticker} 的信号数据"}

    events.sort(key=lambda s: s.event_date, reverse=True)

    return {
        "ticker": ticker.upper(),
        "company_name": events[0].company_name,
        "sector": events[0].sector,
        "total_events": len(events),
        "events": [asdict(e) for e in events],
    }


@app.get("/api/companies")
def get_companies(
    market: str = "us",
    filter: str = Query("company"),
    sort: str = Query("excess"),
    sector: str = Query("all"),
):
    scan = _load_scan(market)
    if scan is None:
        return {"error": "扫描数据不存在，请先运行 run_full.py"}

    signals = scan.signals
    if filter == "company":
        signals = [s for s in signals if s.is_company_specific]
    elif filter == "market":
        signals = [s for s in signals if not s.is_company_specific]

    if sector != "all":
        signals = [s for s in signals if s.sector == sector]

    grouped: dict[str, dict] = {}
    for s in signals:
        t = s.ticker
        if t not in grouped:
            grouped[t] = {
                "ticker": t,
                "company_name": s.company_name,
                "sector": s.sector,
                "total_events": 0,
                "company_events": 0,
                "max_excess_pct": 0.0,
                "avg_excess_pct": 0.0,
                "max_daily_return_pct": 0.0,
                "first_event": s.event_date,
                "last_event": s.event_date,
                "excess_list": [],
            }
        g = grouped[t]
        g["total_events"] += 1
        if s.is_company_specific:
            g["company_events"] += 1
        g["excess_list"].append(s.excess_return_pct)
        if abs(s.excess_return_pct) > abs(g["max_excess_pct"]):
            g["max_excess_pct"] = s.excess_return_pct
        if abs(s.daily_return_pct) > abs(g["max_daily_return_pct"]):
            g["max_daily_return_pct"] = s.daily_return_pct
        if s.event_date < g["first_event"]:
            g["first_event"] = s.event_date
        if s.event_date > g["last_event"]:
            g["last_event"] = s.event_date

    companies = []
    for g in grouped.values():
        exl = g.pop("excess_list")
        g["avg_excess_pct"] = round(sum(abs(e) for e in exl) / len(exl), 2) if exl else 0.0
        g["max_excess_pct"] = round(g["max_excess_pct"], 2)
        g["max_daily_return_pct"] = round(g["max_daily_return_pct"], 2)
        companies.append(g)

    if sort == "excess":
        companies.sort(key=lambda c: abs(c["max_excess_pct"]), reverse=True)
    elif sort == "frequency":
        companies.sort(key=lambda c: c["total_events"], reverse=True)
    elif sort == "avg_excess":
        companies.sort(key=lambda c: c["avg_excess_pct"], reverse=True)
    else:
        companies.sort(key=lambda c: c["last_event"], reverse=True)

    return {
        "market": market,
        "total_companies": len(companies),
        "companies": companies,
    }


@app.get("/api/sectors")
def get_sectors(market: str = "us", filter: str = Query("all")):
    scan = _load_scan(market)
    if scan is None:
        return {"sectors": []}

    signals = scan.signals
    if filter == "company":
        signals = [s for s in signals if s.is_company_specific]
    elif filter == "market":
        signals = [s for s in signals if not s.is_company_specific]

    sector_counts: dict[str, int] = {}
    for s in signals:
        sector_counts[s.sector] = sector_counts.get(s.sector, 0) + 1

    sectors = [
        {"name": name, "event_count": count}
        for name, count in sorted(sector_counts.items(), key=lambda x: -x[1])
    ]
    return {"market": market, "sectors": sectors}


@app.get("/api/stats")
def get_stats(market: str = "us"):
    scan = _load_scan(market)
    bm = _load_benchmark(market)

    if scan is None:
        return {"error": "数据不存在，请先运行 run_full.py"}

    return {
        "market": market,
        "total_scanned": scan.total_scanned,
        "total_triggered": scan.total_triggered,
        "total_events": len(scan.signals),
        "threshold_pct": scan.threshold_pct,
        "scan_date": scan.scan_date,
        "benchmark_companies": bm.metadata.get("num_benchmarks", 0) if bm else 0,
        "benchmark_events": bm.metadata.get("num_events", 0) if bm else 0,
    }
