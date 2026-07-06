"""预缓存港股财报日期到 data/prices/earnings/，带限流避免被 Yahoo 封。

用法：
    python scripts/prefetch_earnings.py          # 拉取全部港股 ticker
    python scripts/prefetch_earnings.py --clear   # 清除空缓存后重新拉取
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CACHE_DIR = ROOT / "data" / "prices" / "earnings"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DELAY = 2.0  # 每个请求间隔秒数


def get_hk_tickers() -> list[str]:
    """从 config 读取所有港股 ticker。"""
    import yaml
    cfg_path = ROOT / "config" / "benchmarks.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return list(cfg["markets"]["hk"].get("sector_mapping", {}).keys())


def main() -> None:
    import yfinance as yf

    clear = "--clear" in sys.argv
    tickers = sorted(get_hk_tickers())

    if clear:
        removed = 0
        for f in CACHE_DIR.glob("*.json"):
            data = json.loads(f.read_text())
            if not data:
                f.unlink()
                removed += 1
        print(f"已清除 {removed} 个空缓存文件")

    total = len(tickers)
    fetched = 0
    skipped = 0
    failed = 0

    print(f"开始预缓存 {total} 只港股的财报日期（间隔 {DELAY}s）...\n")

    for i, ticker in enumerate(tickers, 1):
        cache_file = CACHE_DIR / f"{ticker.replace('.', '_')}.json"

        if cache_file.exists():
            data = json.loads(cache_file.read_text())
            if data:
                skipped += 1
                print(f"  [{i}/{total}] {ticker} — 已缓存 ({len(data)} 条)")
                continue

        try:
            ed = yf.Ticker(ticker).earnings_dates
            if ed is not None and not ed.empty:
                dates = [d.to_pydatetime().replace(tzinfo=None) for d in ed.index]
                date_strs = [d.strftime("%Y-%m-%d") for d in dates]
                cache_file.write_text(json.dumps(date_strs))
                fetched += 1
                print(f"  [{i}/{total}] {ticker} — 获取 {len(dates)} 条财报日期")
            else:
                cache_file.write_text("[]")
                print(f"  [{i}/{total}] {ticker} — 无财报数据")
        except Exception as exc:
            failed += 1
            err_msg = str(exc)[:60]
            print(f"  [{i}/{total}] {ticker} — 失败: {err_msg}")

        if i < total:
            time.sleep(DELAY)

    print(f"\n完成：{fetched} 新获取, {skipped} 已缓存, {failed} 失败 (共 {total})")


if __name__ == "__main__":
    main()
