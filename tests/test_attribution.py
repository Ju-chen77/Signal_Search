"""attribution 新闻归因逻辑测试。"""

import pytest

from src.output.signals import Signal, AttributedSignal, NewsItem


class TestAttribution:
    def test_attributed_signal_from_signal_with_news(self):
        sig = Signal(
            ticker="TSLA", company_name="Tesla", sector="Auto",
            event_date="2023-05-10", daily_return_pct=12.0,
            volume_change_pct=300.0, price_before=170.0, price_after=190.4,
        )
        news = [
            NewsItem(
                title="Tesla announces new model",
                source="Reuters",
                date="2023-05-10",
                url="https://example.com/1",
                summary="Tesla unveiled ...",
            ),
        ]
        attributed = AttributedSignal.from_signal(sig, news)

        assert attributed.attributed is True
        assert len(attributed.news) == 1
        assert attributed.ticker == "TSLA"
        assert attributed.daily_return_pct == 12.0

    def test_attributed_signal_without_news(self):
        sig = Signal(
            ticker="XYZ", company_name="XYZ Corp", sector="Unknown",
            event_date="2023-01-01", daily_return_pct=-9.0,
            volume_change_pct=50.0, price_before=100.0, price_after=91.0,
        )
        attributed = AttributedSignal.from_signal(sig)

        assert attributed.attributed is False
        assert attributed.news == []

    def test_news_item_fields(self):
        item = NewsItem(
            title="Breaking news",
            source="Bloomberg",
            date="2023-06-01",
            url="https://bloomberg.com/article",
            summary="Summary text",
        )
        assert item.title == "Breaking news"
        assert item.source == "Bloomberg"

    def test_deduplication_logic(self):
        raw = [
            {"title": "Stock drops 10%", "source": "A"},
            {"title": "Stock drops 10%", "source": "B"},
            {"title": "Market crash", "source": "C"},
        ]
        seen: set[str] = set()
        deduped = []
        for item in raw:
            key = item["title"].strip().lower()
            if key not in seen:
                seen.add(key)
                deduped.append(item)

        assert len(deduped) == 2
