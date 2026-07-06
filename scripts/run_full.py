"""完整流程：benchmark → scan → attribution → 输出。

用法：python scripts/run_full.py --market us
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analysis.benchmark import calculate_benchmark
from src.analysis.scanner import scan_market
from src.analysis.attribution import attribute_signals


def main() -> None:
    parser = argparse.ArgumentParser(description="完整流程：基准→扫描→归因")
    parser.add_argument("--market", default="us", choices=["us", "hk", "a_share"])
    parser.add_argument("--skip-news", action="store_true", help="跳过新闻归因（加快速度）")
    parser.add_argument("--top", type=int, default=0, help="只对前 N 个信号做新闻归因（0=全部）")
    args = parser.parse_args()

    data_dir = Path(__file__).resolve().parent.parent / "data" / "signals"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Benchmark
    print(f"{'='*50}")
    print(f" Step 1/3: 计算 {args.market.upper()} 市场波动率基准")
    print(f"{'='*50}\n")

    benchmark = calculate_benchmark(args.market)
    benchmark.save(data_dir / f"benchmark_{args.market}.json")
    print(f"\n门槛值: ±{benchmark.threshold_pct}%\n")

    # Step 2: Scan
    print(f"{'='*50}")
    print(f" Step 2/3: 扫描市场")
    print(f"{'='*50}\n")

    result = scan_market(args.market, benchmark)
    print()

    # Step 3: Attribution
    if not args.skip_news and result.signals:
        print(f"{'='*50}")
        print(f" Step 3/3: 新闻归因")
        print(f"{'='*50}\n")

        targets = result.signals
        if args.top > 0:
            targets = sorted(targets, key=lambda s: abs(s.daily_return_pct), reverse=True)[:args.top]
            print(f"只对波动最大的前 {args.top} 个信号做归因\n")

        attribute_signals(targets)
    else:
        print("\n跳过新闻归因\n")

    # 保存最终结果
    out_path = data_dir / f"full_{args.market}.json"
    result.save(out_path)

    print(f"\n{'='*50}")
    print(f" 完成!")
    print(f"{'='*50}")
    print(f"  市场:     {args.market.upper()}")
    print(f"  门槛:     ±{result.threshold_pct}%")
    print(f"  扫描:     {result.total_scanned} 只股票")
    print(f"  触发:     {result.total_triggered} 只股票")
    print(f"  事件:     {len(result.signals)} 个")
    print(f"  结果:     {out_path}")


if __name__ == "__main__":
    main()
