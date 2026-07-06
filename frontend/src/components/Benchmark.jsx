import { useState, useEffect } from "react";
import { fetchBenchmark } from "../utils/api";

export default function Benchmark({ market = "us" }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadBenchmark();
  }, [market]);

  async function loadBenchmark() {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchBenchmark(market);
      setData(result);
    } catch (err) {
      setError(err.message || "Failed to load benchmark data");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-12 flex items-center justify-center">
        <div className="flex items-center gap-3 text-[#64748b]">
          <div className="w-4 h-4 border-2 border-[#3b82f6] border-t-transparent rounded-full animate-spin" />
          <span className="text-sm">Loading benchmark data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="bg-[#1e293b] border border-red-900/50 rounded-lg p-8 max-w-md text-center">
          <div className="text-red-400 text-lg font-medium mb-2">
            Connection Error
          </div>
          <p className="text-[#94a3b8] text-sm mb-4">{error}</p>
          <button
            onClick={loadBenchmark}
            className="px-4 py-2 bg-[#3b82f6] text-white text-sm rounded hover:bg-[#2563eb] transition-colors cursor-pointer"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const events = data.benchmark_events || [];
  const metadata = data.metadata || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Benchmark Analysis
        </h1>
        <p className="text-sm text-[#94a3b8] mt-1">
          Market: {data.market?.toUpperCase()} &nbsp;&middot;&nbsp; Threshold:
          &plusmn;{data.threshold_pct?.toFixed(1)}% daily return
        </p>
      </div>

      {/* Threshold Explanation */}
      <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-6">
        <h2 className="text-sm font-medium text-[#64748b] uppercase tracking-wider mb-3">
          How the Threshold is Calculated
        </h2>
        <div className="text-sm text-[#94a3b8] space-y-2">
          <p>
            The controversy signal threshold is derived from a curated set of
            benchmark companies with well-documented public controversies. By
            analyzing the daily price returns of these companies during their
            known controversy events, we establish a statistical baseline for
            what constitutes an &quot;abnormal&quot; price movement.
          </p>
          <p>
            The current threshold of{" "}
            <span className="text-white font-mono font-semibold">
              &plusmn;{data.threshold_pct?.toFixed(1)}%
            </span>{" "}
            represents the magnitude of daily return that signals a potential
            controversy-driven event. Any stock whose daily return exceeds this
            threshold is flagged for further investigation.
          </p>
          {metadata && Object.keys(metadata).length > 0 && (
            <div className="mt-4 bg-[#0f172a] rounded p-4 border border-[#334155]/50">
              <div className="text-xs text-[#64748b] uppercase tracking-wider mb-2">
                Metadata
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(metadata).map(([key, value]) => (
                  <div key={key} className="flex justify-between gap-2">
                    <span className="text-[#64748b]">{key}:</span>
                    <span className="text-[#e2e8f0] font-mono">
                      {typeof value === "number" ? value.toFixed(2) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Benchmark Events Table */}
      <div className="bg-[#1e293b] border border-[#334155] rounded-lg overflow-hidden">
        <div className="px-5 py-4 border-b border-[#334155]">
          <h2 className="text-sm font-medium text-[#64748b] uppercase tracking-wider">
            Benchmark Controversy Events ({events.length})
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#334155] text-[#64748b] text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3 font-medium">Ticker</th>
                <th className="text-left px-4 py-3 font-medium">Company</th>
                <th className="text-left px-4 py-3 font-medium">Date</th>
                <th className="text-right px-4 py-3 font-medium">
                  Daily Return
                </th>
                <th className="text-right px-4 py-3 font-medium">
                  Close Price
                </th>
                <th className="text-right px-4 py-3 font-medium">Volume</th>
              </tr>
            </thead>
            <tbody>
              {events.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-12 text-center text-[#64748b]"
                  >
                    No benchmark events available
                  </td>
                </tr>
              ) : (
                events.map((event, idx) => (
                  <BenchmarkRow key={idx} event={event} />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Benchmark Companies Summary */}
      <CompanySummary events={events} />
    </div>
  );
}

function BenchmarkRow({ event }) {
  const returnPct = event.daily_return_pct;
  const returnColor = returnPct >= 0 ? "text-[#22c55e]" : "text-[#ef4444]";
  const returnSign = returnPct >= 0 ? "+" : "";

  return (
    <tr className="border-b border-[#334155]/50 hover:bg-[#334155]/40 transition-colors">
      <td className="px-4 py-3">
        <span className="font-mono font-semibold text-[#3b82f6]">
          {event.ticker}
        </span>
      </td>
      <td className="px-4 py-3 text-[#e2e8f0]">{event.company_name}</td>
      <td className="px-4 py-3 font-mono text-[#94a3b8]">{event.date}</td>
      <td
        className={`px-4 py-3 text-right font-mono font-semibold ${returnColor}`}
      >
        {returnSign}
        {returnPct?.toFixed(2)}%
      </td>
      <td className="px-4 py-3 text-right font-mono text-[#94a3b8]">
        {event.close_price?.toFixed(2)}
      </td>
      <td className="px-4 py-3 text-right font-mono text-[#94a3b8]">
        {event.volume?.toLocaleString()}
      </td>
    </tr>
  );
}

function CompanySummary({ events }) {
  // Group events by company
  const byCompany = {};
  events.forEach((e) => {
    if (!byCompany[e.ticker]) {
      byCompany[e.ticker] = {
        ticker: e.ticker,
        company_name: e.company_name,
        events: [],
      };
    }
    byCompany[e.ticker].events.push(e);
  });

  const companies = Object.values(byCompany);
  if (companies.length === 0) return null;

  return (
    <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-6">
      <h2 className="text-sm font-medium text-[#64748b] uppercase tracking-wider mb-4">
        Benchmark Companies ({companies.length})
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {companies.map((company) => {
          const avgReturn =
            company.events.reduce((sum, e) => sum + e.daily_return_pct, 0) /
            company.events.length;
          const worstEvent = company.events.reduce((worst, e) =>
            e.daily_return_pct < worst.daily_return_pct ? e : worst
          );
          return (
            <div
              key={company.ticker}
              className="bg-[#0f172a] border border-[#334155]/50 rounded p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono font-semibold text-[#3b82f6]">
                  {company.ticker}
                </span>
                <span className="text-xs text-[#64748b]">
                  {company.events.length} event
                  {company.events.length !== 1 ? "s" : ""}
                </span>
              </div>
              <div className="text-sm text-[#e2e8f0] mb-2">
                {company.company_name}
              </div>
              <div className="text-xs text-[#64748b] space-y-1">
                <div className="flex justify-between">
                  <span>Avg Return:</span>
                  <span
                    className={`font-mono ${
                      avgReturn >= 0 ? "text-[#22c55e]" : "text-[#ef4444]"
                    }`}
                  >
                    {avgReturn >= 0 ? "+" : ""}
                    {avgReturn.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Worst Day:</span>
                  <span className="font-mono text-[#ef4444]">
                    {worstEvent.daily_return_pct.toFixed(2)}% (
                    {worstEvent.date})
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
