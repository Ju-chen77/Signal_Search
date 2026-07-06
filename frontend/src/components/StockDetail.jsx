import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { fetchSignalDetail } from "../utils/api";

export default function StockDetail({ ticker, market = "us", onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!ticker) return;
    loadDetail();
  }, [ticker, market]);

  async function loadDetail() {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchSignalDetail(ticker, market);
      setData(result);
    } catch (err) {
      setError(err.message || "Failed to load stock detail");
    } finally {
      setLoading(false);
    }
  }

  if (!ticker) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-8 max-w-md text-center">
          <div className="text-[#64748b] text-lg mb-2">No Stock Selected</div>
          <p className="text-[#94a3b8] text-sm mb-4">
            Select a stock from the Dashboard to view its details.
          </p>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-[#3b82f6] text-white text-sm rounded hover:bg-[#2563eb] transition-colors cursor-pointer"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-12 flex items-center justify-center">
        <div className="flex items-center gap-3 text-[#64748b]">
          <div className="w-4 h-4 border-2 border-[#3b82f6] border-t-transparent rounded-full animate-spin" />
          <span className="text-sm">Loading {ticker} details...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="bg-[#1e293b] border border-red-900/50 rounded-lg p-8 max-w-md text-center">
          <div className="text-red-400 text-lg font-medium mb-2">Error</div>
          <p className="text-[#94a3b8] text-sm mb-4">{error}</p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={loadDetail}
              className="px-4 py-2 bg-[#3b82f6] text-white text-sm rounded hover:bg-[#2563eb] transition-colors cursor-pointer"
            >
              Retry
            </button>
            <button
              onClick={onBack}
              className="px-4 py-2 bg-[#334155] text-[#e2e8f0] text-sm rounded hover:bg-[#475569] transition-colors cursor-pointer"
            >
              Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const events = data.events || [];

  // Build chart data from events (sorted by date)
  const chartData = events
    .map((e) => ({
      date: e.event_date,
      priceBefore: e.price_before,
      priceAfter: e.price_after,
      returnPct: e.daily_return_pct,
    }))
    .sort((a, b) => a.date.localeCompare(b.date));

  // Build a combined price series for the chart:
  // For each event, show both the price_before and price_after as two data points
  const priceSeries = [];
  chartData.forEach((d) => {
    priceSeries.push({
      date: d.date + " Open",
      price: d.priceBefore,
      dateLabel: d.date,
    });
    priceSeries.push({
      date: d.date + " Close",
      price: d.priceAfter,
      dateLabel: d.date,
    });
  });

  return (
    <div className="space-y-6">
      {/* Back button + Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={onBack}
          className="text-[#94a3b8] hover:text-white transition-colors text-sm cursor-pointer"
        >
          &larr; Back to Dashboard
        </button>
      </div>

      {/* Company Info */}
      <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-6">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">
              <span className="text-[#3b82f6] font-mono">{data.ticker}</span>
              <span className="text-[#64748b] mx-2">/</span>
              {data.company_name}
            </h1>
            <p className="text-sm text-[#94a3b8] mt-1">
              Sector: {data.sector || "N/A"} &nbsp;&middot;&nbsp;{" "}
              {events.length} controversy event{events.length !== 1 ? "s" : ""}
            </p>
          </div>
        </div>
      </div>

      {/* Price Chart */}
      {priceSeries.length > 0 && (
        <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-6">
          <h2 className="text-sm font-medium text-[#64748b] uppercase tracking-wider mb-4">
            Price at Controversy Events
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={priceSeries}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="dateLabel"
                stroke="#64748b"
                tick={{ fontSize: 11 }}
                tickFormatter={(v, i) => (i % 2 === 0 ? v : "")}
              />
              <YAxis
                stroke="#64748b"
                tick={{ fontSize: 11 }}
                domain={["auto", "auto"]}
                tickFormatter={(v) => `${market === "hk" ? "HK$" : "$"}${v.toFixed(0)}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "6px",
                  color: "#e2e8f0",
                  fontSize: "12px",
                }}
                formatter={(value) => [`${market === "hk" ? "HK$" : "$"}${value.toFixed(2)}`, "Price"]}
              />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: "#3b82f6", r: 4 }}
                activeDot={{ r: 6, fill: "#60a5fa" }}
              />
              {/* Add reference lines for each event date */}
              {chartData.map((d) => (
                <ReferenceLine
                  key={d.date}
                  x={d.date + " Open"}
                  stroke={d.returnPct < 0 ? "#ef4444" : "#22c55e"}
                  strokeDasharray="3 3"
                  strokeOpacity={0.6}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Event Timeline */}
      <div className="space-y-4">
        <h2 className="text-sm font-medium text-[#64748b] uppercase tracking-wider">
          Event Timeline
        </h2>
        {events.length === 0 ? (
          <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-8 text-center text-[#64748b]">
            No events found for this stock.
          </div>
        ) : (
          events
            .sort((a, b) => b.event_date.localeCompare(a.event_date))
            .map((event, idx) => <EventCard key={idx} event={event} />)
        )}
      </div>
    </div>
  );
}

function EventCard({ event }) {
  const returnPct = event.daily_return_pct;
  const returnColor = returnPct >= 0 ? "text-[#22c55e]" : "text-[#ef4444]";
  const returnBg = returnPct >= 0 ? "bg-green-900/20" : "bg-red-900/20";
  const returnSign = returnPct >= 0 ? "+" : "";

  return (
    <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-5">
      {/* Event header */}
      <div className="flex flex-wrap items-center gap-4 mb-4">
        <span className="font-mono text-sm text-[#94a3b8]">
          {event.event_date}
        </span>
        <span
          className={`px-2.5 py-1 rounded text-sm font-mono font-semibold ${returnColor} ${returnBg}`}
        >
          {returnSign}
          {returnPct?.toFixed(2)}%
        </span>
        <span className="text-xs text-[#64748b]">
          {event.price_before?.toFixed(2)} &rarr;{" "}
          {event.price_after?.toFixed(2)}
        </span>
        {event.volume_change_pct != null && (
          <span className="text-xs text-[#64748b]">
            Vol: +{event.volume_change_pct.toFixed(0)}%
          </span>
        )}
        {event.excess_return_pct != null && event.excess_return_pct !== 0 && (
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${
            event.is_company_specific
              ? "bg-[#f59e0b]/20 text-[#fbbf24]"
              : "bg-[#64748b]/20 text-[#94a3b8]"
          }`}>
            {event.is_company_specific ? "公司特有" : `跟随${event.sector_index || "大盘"}`}
            {" "}超额{event.excess_return_pct > 0 ? "+" : ""}{event.excess_return_pct.toFixed(1)}%
          </span>
        )}
        {event.sector_index && event.sector_index !== "HSI" && (
          <span className="text-xs text-[#64748b]">
            对标 {event.sector_index} {event.market_return_pct != null ? `${event.market_return_pct > 0 ? "+" : ""}${event.market_return_pct.toFixed(1)}%` : ""}
          </span>
        )}
        {event.near_earnings && (
          <span
            className="px-2 py-0.5 rounded text-xs font-medium bg-[#8b5cf6]/20 text-[#a78bfa]"
            title={`财报日: ${event.earnings_date}`}
          >
            财报 {event.earnings_date}
          </span>
        )}
        {event.attributed && (
          <span className="px-2 py-0.5 rounded text-xs bg-[#3b82f6]/20 text-[#60a5fa] font-medium">
            Attributed
          </span>
        )}
      </div>

      {/* News list */}
      {event.news && event.news.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs text-[#64748b] uppercase tracking-wider mb-1">
            Related News
          </div>
          {event.news.map((n, nIdx) => (
            <div
              key={nIdx}
              className="bg-[#0f172a] rounded p-3 border border-[#334155]/50"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  {n.url ? (
                    <a
                      href={n.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-[#e2e8f0] hover:text-[#3b82f6] transition-colors"
                    >
                      {n.title}
                    </a>
                  ) : (
                    <span className="text-sm text-[#e2e8f0]">{n.title}</span>
                  )}
                  {n.summary && (
                    <p className="text-xs text-[#94a3b8] mt-1 line-clamp-2">
                      {n.summary}
                    </p>
                  )}
                </div>
                <div className="text-right shrink-0">
                  {n.source && (
                    <div className="text-xs text-[#64748b]">{n.source}</div>
                  )}
                  {n.date && (
                    <div className="text-xs text-[#64748b]">{n.date}</div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
