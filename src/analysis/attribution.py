"""波动事件归因：为每个触发信号匹配对应的新闻。"""

from __future__ import annotations

from src.data.news_client import get_news_for_event
from src.output.signals import AttributedSignal, NewsItem


def attribute_signals(signals: list[AttributedSignal]) -> list[AttributedSignal]:
    """对每个信号事件查找新闻进行归因。"""
    total = len(signals)
    attributed_count = 0

    for i, sig in enumerate(signals, 1):
        if i % 20 == 0 or i == 1:
            print(f"[attribution] 归因进度 {i}/{total}")

        try:
            raw_news = get_news_for_event(sig.ticker, sig.event_date)
            news_items = [
                NewsItem(
                    title=n.get("title", ""),
                    source=n.get("source", ""),
                    date=n.get("date", ""),
                    url=n.get("url", ""),
                    summary=n.get("summary", ""),
                )
                for n in raw_news
            ]
            sig.news = news_items
            sig.attributed = len(news_items) > 0
            if sig.attributed:
                attributed_count += 1
        except Exception as exc:
            print(f"[attribution] {sig.ticker} ({sig.event_date}) 归因失败: {exc}")
            sig.attributed = False

    print(f"[attribution] 完成：{attributed_count}/{total} 个事件已归因")
    return signals
