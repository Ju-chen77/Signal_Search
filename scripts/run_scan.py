"""用 benchmark 基准扫描市场。

用法：python scripts/run_scan.py --market us
前置条件：已运行 run_benchmark.py
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analysis.scanner import scan_market
from src.output.signals import BenchmarkResult


def main() -> None:
    parser = argparse.ArgumentParser(description="扫描市场寻找争议波动信号")
    parser.add_argument("--market", default="us", choices=["us", "hk", "a_share"])
    args = parser.parse_args()

    data_dir = Path(__file__).resolve().parent.parent / "data" / "signals"
    bm_path = data_dir / f"benchmark_{args.market}.json"

    if not bm_path.exists():
        print(f"错误：请先运行 run_benchmark.py --market {args.market}")
        sys.exit(1)

    benchmark = BenchmarkResult.load(bm_path)
    print(f"=== 扫描 {args.market.upper()} 市场（门槛 ±{benchmark.threshold_pct}%）===\n")

    result = scan_market(args.market, benchmark)

    out_path = data_dir / f"scan_{args.market}.json"
    result.save(out_path)
    print(f"\n结果已保存到 {out_path}")


if __name__ == "__main__":
    main()
