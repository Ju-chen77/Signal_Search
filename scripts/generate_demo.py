"""生成演示数据，让前端可以立即展示效果。

用法：python scripts/generate_demo.py
生成后直接启动 API + 前端就能看到完整界面。
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dataclasses import asdict
from src.output.signals import (
    BenchmarkEvent, BenchmarkResult,
    NewsItem, AttributedSignal, ScanResult,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "signals"


def generate_benchmark() -> BenchmarkResult:
    events = [
        BenchmarkEvent("AAPL", "Apple", "2024-08-05", -4.82, 209.27, 119548600),
        BenchmarkEvent("AAPL", "Apple", "2024-01-18", -3.36, 185.56, 58375000),
        BenchmarkEvent("AAPL", "Apple", "2022-09-13", -5.87, 153.84, 122656600),
        BenchmarkEvent("AAPL", "Apple", "2022-06-13", -3.83, 131.88, 107961300),
        BenchmarkEvent("AMZN", "Amazon", "2024-08-02", -8.78, 167.90, 112488800),
        BenchmarkEvent("AMZN", "Amazon", "2024-02-02", 7.87, 171.81, 81726600),
        BenchmarkEvent("AMZN", "Amazon", "2022-11-09", -5.09, 91.56, 86000000),
        BenchmarkEvent("AMZN", "Amazon", "2022-04-29", -14.05, 2485.63, 31300000),
        BenchmarkEvent("TSLA", "Tesla", "2024-07-24", -12.33, 215.99, 119548600),
        BenchmarkEvent("TSLA", "Tesla", "2024-04-24", 12.06, 162.13, 135000000),
        BenchmarkEvent("TSLA", "Tesla", "2024-01-25", -12.13, 182.63, 106791300),
        BenchmarkEvent("TSLA", "Tesla", "2023-07-20", -9.74, 262.90, 152117700),
        BenchmarkEvent("TSLA", "Tesla", "2023-01-26", 11.00, 160.27, 200000000),
        BenchmarkEvent("TSLA", "Tesla", "2022-10-25", -6.65, 207.28, 84000000),
        BenchmarkEvent("NFLX", "Netflix", "2024-07-19", -6.09, 631.30, 18700000),
        BenchmarkEvent("NFLX", "Netflix", "2024-01-24", 10.73, 549.19, 25700000),
        BenchmarkEvent("NFLX", "Netflix", "2023-07-20", -8.41, 437.92, 17000000),
        BenchmarkEvent("NFLX", "Netflix", "2022-04-20", -35.12, 226.19, 50000000),
        BenchmarkEvent("NVDA", "Nvidia", "2024-09-03", -9.53, 108.00, 327700000),
        BenchmarkEvent("NVDA", "Nvidia", "2024-07-24", -6.80, 112.28, 228000000),
        BenchmarkEvent("NVDA", "Nvidia", "2024-05-23", 9.32, 1037.99, 64000000),
        BenchmarkEvent("NVDA", "Nvidia", "2024-02-22", 16.40, 785.38, 82600000),
        BenchmarkEvent("NVDA", "Nvidia", "2023-05-25", 24.37, 379.80, 97600000),
        BenchmarkEvent("META", "Meta", "2024-04-25", -10.56, 441.38, 62100000),
        BenchmarkEvent("META", "Meta", "2024-02-02", 20.32, 474.99, 103600000),
        BenchmarkEvent("META", "Meta", "2023-04-27", 13.93, 238.29, 79500000),
        BenchmarkEvent("META", "Meta", "2022-10-27", -24.56, 97.94, 94700000),
        BenchmarkEvent("META", "Meta", "2022-02-03", -26.39, 237.76, 128900000),
    ]

    return BenchmarkResult(
        market="us",
        threshold_pct=3.36,
        benchmark_events=events,
        metadata={
            "lookback_years": 5,
            "percentile": 99,
            "num_benchmarks": 6,
            "num_events": len(events),
        },
    )


def generate_signals() -> ScanResult:
    signals = [
        # 科技股大波动
        _sig("SMCI", "Super Micro Computer", "Technology", "2024-08-06", -6.73, 280.0, 543.21, 506.65, [
            _news("Super Micro plunges on DOJ investigation reports", "Bloomberg", "2024-08-06"),
            _news("SMCI accounting practices questioned by short seller", "Hindenburg Research", "2024-08-05"),
        ]),
        _sig("INTC", "Intel Corp", "Technology", "2024-08-02", -26.06, 420.0, 29.05, 21.48, [
            _news("Intel suspends dividend, announces massive layoffs", "Reuters", "2024-08-01"),
            _news("Intel reports worst quarterly results in decades", "CNBC", "2024-08-01"),
        ]),
        _sig("CRM", "Salesforce", "Technology", "2024-05-30", -19.74, 350.0, 272.50, 218.72, [
            _news("Salesforce misses revenue expectations, shares plummet", "Wall Street Journal", "2024-05-30"),
        ]),
        _sig("SNAP", "Snap Inc", "Technology", "2024-02-07", -32.66, 500.0, 17.16, 11.55, [
            _news("Snap reports weak ad revenue outlook", "Bloomberg", "2024-02-06"),
        ]),
        _sig("AMD", "Advanced Micro Devices", "Technology", "2024-07-31", -6.17, 180.0, 148.50, 139.34, [
            _news("AMD AI chip revenue disappoints Wall Street expectations", "Reuters", "2024-07-30"),
        ]),

        # 金融股
        _sig("SCHW", "Charles Schwab", "Financial Services", "2024-01-17", -4.51, 200.0, 68.12, 65.05, [
            _news("Schwab reports client cash sorting continues", "Financial Times", "2024-01-16"),
        ]),
        _sig("JPM", "JPMorgan Chase", "Financial Services", "2024-04-12", -6.47, 150.0, 198.57, 185.73, [
            _news("JPMorgan warns of higher expenses, net interest income concerns", "CNBC", "2024-04-12"),
        ]),

        # 医药/生物
        _sig("MRNA", "Moderna", "Healthcare", "2024-08-02", -12.35, 300.0, 119.50, 104.74, [
            _news("Moderna slashes 2024 sales forecast amid declining vaccine demand", "Reuters", "2024-08-01"),
        ]),
        _sig("PFE", "Pfizer", "Healthcare", "2024-07-31", -5.02, 250.0, 30.15, 28.64, [
            _news("Pfizer cuts annual forecast, COVID drug sales disappoint", "Bloomberg", "2024-07-30"),
        ]),
        _sig("LLY", "Eli Lilly", "Healthcare", "2024-04-30", -6.25, 180.0, 792.86, 743.30, [
            _news("Lilly shares drop despite raising full-year outlook", "Wall Street Journal", "2024-04-30"),
        ]),

        # 消费
        _sig("NKE", "Nike", "Consumer Cyclical", "2024-06-28", -19.98, 400.0, 94.50, 75.62, [
            _news("Nike issues shocking revenue warning, shares crater", "CNBC", "2024-06-28"),
            _news("Nike CEO admits company lost focus on running category", "Wall Street Journal", "2024-06-28"),
        ]),
        _sig("LULU", "Lululemon", "Consumer Cyclical", "2024-03-22", -15.83, 350.0, 452.10, 380.53, [
            _news("Lululemon gives weak guidance as growth slows", "Reuters", "2024-03-21"),
        ]),
        _sig("SBUX", "Starbucks", "Consumer Cyclical", "2024-05-01", -15.88, 280.0, 84.35, 70.95, [
            _news("Starbucks reports first sales decline since COVID", "Bloomberg", "2024-04-30"),
        ]),

        # 能源
        _sig("OXY", "Occidental Petroleum", "Energy", "2024-08-05", -7.82, 190.0, 57.20, 52.73, [
            _news("Oil prices crash as global demand concerns mount", "Reuters", "2024-08-05"),
        ]),
        _sig("DVN", "Devon Energy", "Energy", "2024-02-22", -5.17, 150.0, 44.73, 42.42, [
            _news("Devon Energy misses earnings, cuts production outlook", "Bloomberg", "2024-02-21"),
        ]),

        # 工业
        _sig("BA", "Boeing", "Industrials", "2024-01-08", -8.03, 250.0, 249.00, 228.99, [
            _news("FAA grounds Boeing 737 MAX 9 after Alaska Airlines door plug blowout", "Reuters", "2024-01-06"),
            _news("Boeing faces new safety crisis as MAX groundings expand", "New York Times", "2024-01-07"),
        ]),
        _sig("UPS", "United Parcel Service", "Industrials", "2024-01-30", -12.05, 300.0, 152.80, 134.38, [
            _news("UPS plans to cut 12,000 jobs as package volumes decline", "CNBC", "2024-01-30"),
        ]),

        # 通信
        _sig("DIS", "Walt Disney", "Communication Services", "2024-02-07", 11.49, 280.0, 96.23, 107.29, [
            _news("Disney reports surprise streaming profit, announces $3B cost cuts", "Bloomberg", "2024-02-07"),
        ]),
        _sig("GOOGL", "Alphabet", "Communication Services", "2024-07-24", -5.04, 150.0, 179.63, 170.58, [
            _news("Alphabet YouTube ad revenue misses expectations", "Wall Street Journal", "2024-07-23"),
        ]),

        # 更多事件
        _sig("TSLA", "Tesla", "Consumer Cyclical", "2024-07-24", -12.33, 350.0, 246.38, 215.99, [
            _news("Tesla reports 45% profit decline, margins hit new low", "Reuters", "2024-07-23"),
            _news("Tesla's Cybertruck recall adds to Musk's mounting problems", "Bloomberg", "2024-07-23"),
        ]),
        _sig("TSLA", "Tesla", "Consumer Cyclical", "2024-04-24", 12.06, 380.0, 144.68, 162.13, [
            _news("Tesla announces affordable model plans, shares surge", "CNBC", "2024-04-23"),
        ]),
        _sig("META", "Meta Platforms", "Communication Services", "2024-04-25", -10.56, 200.0, 493.50, 441.38, [
            _news("Meta spooks investors with massive AI spending plans", "Financial Times", "2024-04-25"),
        ]),
        _sig("META", "Meta Platforms", "Communication Services", "2024-02-02", 20.32, 400.0, 394.78, 474.99, [
            _news("Meta announces first-ever dividend, shares rocket", "Reuters", "2024-02-01"),
            _news("Meta reports blowout earnings, ad business rebounding", "CNBC", "2024-02-01"),
        ]),
        _sig("NVDA", "Nvidia", "Technology", "2024-09-03", -9.53, 200.0, 119.37, 108.00, [
            _news("Nvidia hit by DOJ antitrust probe into AI chip dominance", "Bloomberg", "2024-09-03"),
        ]),
        _sig("NVDA", "Nvidia", "Technology", "2024-02-22", 16.40, 350.0, 674.72, 785.38, [
            _news("Nvidia earnings triple, data center revenue up 409%", "Reuters", "2024-02-21"),
            _news("Jensen Huang declares 'new industrial revolution' driven by AI", "CNBC", "2024-02-21"),
        ]),
    ]

    return ScanResult(
        market="us",
        threshold_pct=3.36,
        scan_date="2024-09-15",
        total_scanned=503,
        total_triggered=47,
        signals=signals,
    )


def _sig(ticker, name, sector, date, ret, vol_chg, price_b, price_a, news_list,
         market_ret=0.0):
    excess = round(ret - market_ret, 2)
    return AttributedSignal(
        ticker=ticker, company_name=name, sector=sector,
        event_date=date, daily_return_pct=ret,
        volume_change_pct=vol_chg, price_before=price_b, price_after=price_a,
        news=[NewsItem(**n) for n in news_list],
        attributed=len(news_list) > 0,
        market_return_pct=market_ret,
        excess_return_pct=excess,
        is_company_specific=abs(excess) > abs(market_ret),
    )


def _news(title, source, date):
    return {"title": title, "source": source, "date": date, "url": "", "summary": ""}


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    bm = generate_benchmark()
    bm.save(DATA_DIR / "benchmark_us.json")
    print(f"[demo] benchmark 数据已生成：{len(bm.benchmark_events)} 个事件，门槛 ±{bm.threshold_pct}%")

    scan = generate_signals()
    scan.save(DATA_DIR / "full_us.json")
    print(f"[demo] 信号数据已生成：{len(scan.signals)} 个事件")
    print(f"\n数据保存在 {DATA_DIR}/")
    print("现在可以启动 API 和前端查看效果了！")


if __name__ == "__main__":
    main()
