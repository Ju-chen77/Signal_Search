"""信号数据结构与 JSON 导出。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class BenchmarkEvent:
    ticker: str
    company_name: str
    date: str
    daily_return_pct: float
    close_price: float
    volume: int


@dataclass
class BenchmarkResult:
    market: str
    threshold_pct: float
    benchmark_events: list[BenchmarkEvent]
    metadata: dict = field(default_factory=dict)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "BenchmarkResult":
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["benchmark_events"] = [BenchmarkEvent(**e) for e in raw["benchmark_events"]]
        return cls(**raw)


@dataclass
class NewsItem:
    title: str
    source: str
    date: str
    url: str
    summary: str = ""


@dataclass
class Signal:
    ticker: str
    company_name: str
    sector: str
    event_date: str
    daily_return_pct: float
    volume_change_pct: float
    price_before: float
    price_after: float
    market_return_pct: float = 0.0
    excess_return_pct: float = 0.0
    is_company_specific: bool = True
    sector_index: str = "HSI"
    near_earnings: bool = False
    earnings_date: str = ""


@dataclass
class AttributedSignal:
    ticker: str
    company_name: str
    sector: str
    event_date: str
    daily_return_pct: float
    volume_change_pct: float
    price_before: float
    price_after: float
    market_return_pct: float = 0.0
    excess_return_pct: float = 0.0
    is_company_specific: bool = True
    sector_index: str = "HSI"
    near_earnings: bool = False
    earnings_date: str = ""
    news: list[NewsItem] = field(default_factory=list)
    attributed: bool = False

    @classmethod
    def from_signal(cls, sig: Signal, news: list[NewsItem] | None = None) -> "AttributedSignal":
        items = news or []
        return cls(
            ticker=sig.ticker,
            company_name=sig.company_name,
            sector=sig.sector,
            event_date=sig.event_date,
            daily_return_pct=sig.daily_return_pct,
            volume_change_pct=sig.volume_change_pct,
            price_before=sig.price_before,
            price_after=sig.price_after,
            market_return_pct=sig.market_return_pct,
            excess_return_pct=sig.excess_return_pct,
            is_company_specific=sig.is_company_specific,
            sector_index=sig.sector_index,
            near_earnings=sig.near_earnings,
            earnings_date=sig.earnings_date,
            news=items,
            attributed=len(items) > 0,
        )


@dataclass
class ScanResult:
    market: str
    threshold_pct: float
    scan_date: str
    total_scanned: int
    total_triggered: int
    signals: list[AttributedSignal] = field(default_factory=list)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "ScanResult":
        raw = json.loads(path.read_text(encoding="utf-8"))
        sigs: list[AttributedSignal] = []
        for s in raw.pop("signals", []):
            news = [NewsItem(**n) for n in s.pop("news", [])]
            s.setdefault("market_return_pct", 0.0)
            s.setdefault("excess_return_pct", 0.0)
            s.setdefault("is_company_specific", True)
            s.setdefault("sector_index", "HSI")
            s.setdefault("near_earnings", False)
            s.setdefault("earnings_date", "")
            sigs.append(AttributedSignal(**s, news=news))
        return cls(**raw, signals=sigs)
