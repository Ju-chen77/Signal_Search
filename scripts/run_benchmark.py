"""计算指定市场的波动率基准。

用法：python scripts/run_benchmark.py --market us
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analysis.benchmark import calculate_benchmark


def main() -> None:
    parser = argparse.ArgumentParser(description="计算 benchmark 波动率基准")
    parser.add_argument("--market", default="us", choices=["us", "hk", "a_share"])
    args = parser.parse_args()

    print(f"=== 计算 {args.market.upper()} 市场波动率基准 ===\n")
    result = calculate_benchmark(args.market)

    out_dir = Path(__file__).resolve().parent.parent / "data" / "signals"
    out_path = out_dir / f"benchmark_{args.market}.json"
    result.save(out_path)
    print(f"\n结果已保存到 {out_path}")
    print(f"波动率门槛: ±{result.threshold_pct}%")


if __name__ == "__main__":
    main()
