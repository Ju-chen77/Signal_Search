import { useState, useEffect } from "react";
import { fetchSignals, fetchStats, fetchCompanies, fetchSectors } from "../utils/api";

const SORT_OPTIONS = [
  { value: "recent", label: "Most Recent" },
  { value: "magnitude", label: "Largest Move" },
  { value: "excess", label: "Largest Excess" },
  { value: "frequency", label: "Most Frequent" },
];

const FILTER_OPTIONS = [
  { value: "all", label: "All Events" },
  { value: "company", label: "Company-Specific" },
  { value: "market", label: "Market-Wide" },
];

const VIEW_OPTIONS = [
  { value: "events", label: "Events" },
  { value: "companies", label: "Companies" },
];

const COMPANY_SORT_OPTIONS = [
  { value: "frequency", label: "Most Frequent" },
  { value: "excess", label: "Max Excess" },
  { value: "avg_excess", label: "Avg Excess" },
  { value: "recent", label: "Most Recent" },
];

export default function Dashboard({ onSelectTicker, market = "us" }) {
  const [signals, setSignals] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sort, setSort] = useState("recent");
  const [sectorFilter, setSectorFilter] = useState("all");
  const [eventFilter, setEventFilter] = useState("all");
  const [page, setPage] = useState(0);
  const [totalEvents, setTotalEvents] = useState(0);
  const [view, setView] = useState("events");
  const [companies, setCompanies] = useState([]);
  const [companySort, setCompanySort] = useState("frequency");
  const [sectors, setSectors] = useState([]);
  const PAGE_SIZE = 50;

  useEffect(() => {
    setPage(0);
  }, [sort, market, eventFilter, view, companySort, sectorFilter]);

  useEffect(() => {
    loadData();
  }, [sort, market, eventFilter, page, view, companySort, sectorFilter]);

  useEffect(() => {
    fetchSectors(market, eventFilter).then((data) => setSectors(data.sectors || [])).catch(() => {});
    setSectorFilter("all");
  }, [market, eventFilter]);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const statsData = await fetchStats(market);
      setStats(statsData);

      if (view === "companies") {
        const compData = await fetchCompanies({ market, filter: eventFilter === "market" ? "market" : "company", sort: companySort, sector: sectorFilter });
        setCompanies(compData.companies || []);
        setTotalEvents(compData.total_companies || 0);
      } else {
        const signalsData = await fetchSignals({ market, sort, filter: eventFilter, limit: PAGE_SIZE, offset: page * PAGE_SIZE, sector: sectorFilter });
        setSignals(signalsData.signals || []);
        setTotalEvents(signalsData.total_events || 0);
      }
    } catch (err) {
      setError(err.message || "Failed to load data");
    } finally {
      setLoading(false);
    }
  }

  const totalPages = view === "events" ? Math.ceil(totalEvents / PAGE_SIZE) : 1;

  function exportPDF() {
    const title = `争议信号雷达 — ${market.toUpperCase()} ${view === "companies" ? "公司汇总" : "事件列表"}`;
    const subtitle = stats
      ? `门槛: ±${stats.threshold_pct?.toFixed(1)}%  |  扫描日期: ${stats.scan_date}  |  ${view === "companies" ? `${companies.length} 家公司` : `${totalEvents} 个事件 (第 ${page + 1} 页)`}`
      : "";

    let rows = "";
    if (view === "companies") {
      rows = `<tr style="background:#1e293b;color:#94a3b8;font-size:11px">
        <th style="padding:6px 10px;text-align:left">代码</th>
        <th style="padding:6px 10px;text-align:left">公司</th>
        <th style="padding:6px 10px;text-align:left">行业</th>
        <th style="padding:6px 10px;text-align:right">次数</th>
        <th style="padding:6px 10px;text-align:right">最大超额</th>
        <th style="padding:6px 10px;text-align:right">平均|超额|</th>
        <th style="padding:6px 10px;text-align:right">最大波动</th>
        <th style="padding:6px 10px;text-align:left">首次</th>
        <th style="padding:6px 10px;text-align:left">最近</th>
      </tr>`;
      for (const c of companies) {
        const ec = c.max_excess_pct >= 0 ? "color:#22c55e" : "color:#ef4444";
        const mc = c.max_daily_return_pct >= 0 ? "color:#22c55e" : "color:#ef4444";
        rows += `<tr style="border-bottom:1px solid #eee">
          <td style="padding:5px 10px;font-family:monospace;font-weight:600">${c.ticker}</td>
          <td style="padding:5px 10px">${c.company_name}</td>
          <td style="padding:5px 10px;font-size:11px">${c.sector}</td>
          <td style="padding:5px 10px;text-align:right;font-weight:700;color:#f59e0b">${c.total_events}</td>
          <td style="padding:5px 10px;text-align:right;font-family:monospace;${ec}">${c.max_excess_pct >= 0 ? "+" : ""}${c.max_excess_pct?.toFixed(1)}%</td>
          <td style="padding:5px 10px;text-align:right;font-family:monospace">${c.avg_excess_pct?.toFixed(1)}%</td>
          <td style="padding:5px 10px;text-align:right;font-family:monospace;${mc}">${c.max_daily_return_pct >= 0 ? "+" : ""}${c.max_daily_return_pct?.toFixed(1)}%</td>
          <td style="padding:5px 10px;font-family:monospace;font-size:11px">${c.first_event}</td>
          <td style="padding:5px 10px;font-family:monospace;font-size:11px">${c.last_event}</td>
        </tr>`;
      }
    } else {
      rows = `<tr style="background:#1e293b;color:#94a3b8;font-size:11px">
        <th style="padding:6px 10px;text-align:left">代码</th>
        <th style="padding:6px 10px;text-align:left">公司</th>
        <th style="padding:6px 10px;text-align:left">行业</th>
        <th style="padding:6px 10px;text-align:left">日期</th>
        <th style="padding:6px 10px;text-align:right">涨跌幅</th>
        <th style="padding:6px 10px;text-align:right">行业指数</th>
        <th style="padding:6px 10px;text-align:right">超额</th>
        <th style="padding:6px 10px;text-align:center">判定</th>
      </tr>`;
      for (const s of signals) {
        const rc = s.daily_return_pct >= 0 ? "color:#22c55e" : "color:#ef4444";
        const ec = (s.excess_return_pct ?? 0) >= 0 ? "color:#22c55e" : "color:#ef4444";
        const isComp = s.is_company_specific !== false;
        const idx = s.sector_index || "HSI";
        const typeTag = isComp
          ? `<span style="background:#fef3c7;color:#92400e;padding:1px 6px;border-radius:3px;font-size:10px">公司特有</span>`
          : `<span style="background:#e2e8f0;color:#475569;padding:1px 6px;border-radius:3px;font-size:10px">跟随${idx}</span>`;
        const earningsTag = s.near_earnings
          ? ` <span style="background:#ede9fe;color:#6d28d9;padding:1px 6px;border-radius:3px;font-size:10px">财报${s.earnings_date ? " " + s.earnings_date : ""}</span>`
          : "";
        rows += `<tr style="border-bottom:1px solid #eee">
          <td style="padding:5px 10px;font-family:monospace;font-weight:600">${s.ticker}</td>
          <td style="padding:5px 10px">${s.company_name}</td>
          <td style="padding:5px 10px;font-size:11px">${s.sector}</td>
          <td style="padding:5px 10px;font-family:monospace">${s.event_date}</td>
          <td style="padding:5px 10px;text-align:right;font-family:monospace;font-weight:600;${rc}">${s.daily_return_pct >= 0 ? "+" : ""}${s.daily_return_pct?.toFixed(2)}%</td>
          <td style="padding:5px 10px;text-align:right;font-family:monospace"><span style="color:#94a3b8;font-size:10px">${idx} </span>${((s.market_return_pct ?? 0) >= 0 ? "+" : "") + (s.market_return_pct ?? 0)?.toFixed(2)}%</td>
          <td style="padding:5px 10px;text-align:right;font-family:monospace;font-weight:600;${ec}">${((s.excess_return_pct ?? 0) >= 0 ? "+" : "") + (s.excess_return_pct ?? 0)?.toFixed(2)}%</td>
          <td style="padding:5px 10px;text-align:center">${typeTag}${earningsTag}</td>
        </tr>`;
      }
    }

    const html = `<!DOCTYPE html><html><head><meta charset="utf-8">
      <title>${title}</title>
      <style>
        body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; margin: 20px; color: #1e293b; }
        h1 { font-size: 18px; margin: 0 0 4px; }
        p { font-size: 12px; color: #64748b; margin: 0 0 16px; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        @media print { body { margin: 10mm; } }
      </style>
    </head><body>
      <h1>${title}</h1>
      <p>${subtitle}</p>
      <table>${rows}</table>
    </body></html>`;

    const w = window.open("", "_blank");
    w.document.write(html);
    w.document.close();
    w.onload = () => { w.print(); };
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
            onClick={loadData}
            className="px-4 py-2 bg-[#3b82f6] text-white text-sm rounded hover:bg-[#2563eb] transition-colors cursor-pointer"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Controversy Signal Radar
          </h1>
          {stats && (
            <p className="text-sm text-[#94a3b8] mt-1">
              Threshold: &plusmn;{stats.threshold_pct?.toFixed(1)}% daily return
              &nbsp;&middot;&nbsp; Market: {stats.market?.toUpperCase()}
              &nbsp;&middot;&nbsp; Scan date: {stats.scan_date}
              {market === "us" && (
                <span className="ml-2 px-2 py-0.5 rounded text-xs bg-yellow-900/40 text-yellow-400 font-medium">
                  Demo Data
                </span>
              )}
            </p>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard
            label="Stocks Scanned"
            value={stats.total_scanned?.toLocaleString()}
          />
          <StatCard
            label="Signals Triggered"
            value={stats.total_triggered?.toLocaleString()}
            accent
          />
          <StatCard
            label="Threshold"
            value={`±${stats.threshold_pct?.toFixed(1)}%`}
          />
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <label className="text-xs text-[#64748b] uppercase tracking-wider">
            View
          </label>
          <div className="flex gap-1">
            {VIEW_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setView(opt.value)}
                className={`px-3 py-1.5 text-xs font-bold rounded transition-colors cursor-pointer ${
                  view === opt.value
                    ? "bg-[#3b82f6] text-white"
                    : "text-[#94a3b8] hover:text-[#e2e8f0] hover:bg-[#334155] border border-[#334155]"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs text-[#64748b] uppercase tracking-wider">
            Sort
          </label>
          <select
            value={view === "companies" ? companySort : sort}
            onChange={(e) => view === "companies" ? setCompanySort(e.target.value) : setSort(e.target.value)}
            className="bg-[#1e293b] border border-[#334155] text-[#e2e8f0] text-sm rounded px-3 py-1.5 focus:outline-none focus:border-[#3b82f6]"
          >
            {(view === "companies" ? COMPANY_SORT_OPTIONS : SORT_OPTIONS).map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        {view === "events" && (
          <div className="flex items-center gap-2">
            <label className="text-xs text-[#64748b] uppercase tracking-wider">
              Type
            </label>
            <div className="flex gap-1">
              {FILTER_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setEventFilter(opt.value)}
                  className={`px-3 py-1.5 text-xs font-medium rounded transition-colors cursor-pointer ${
                    eventFilter === opt.value
                      ? opt.value === "company"
                        ? "bg-[#f59e0b] text-[#0f172a]"
                        : opt.value === "market"
                          ? "bg-[#64748b] text-white"
                          : "bg-[#3b82f6] text-white"
                      : "text-[#94a3b8] hover:text-[#e2e8f0] hover:bg-[#334155] border border-[#334155]"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        )}
        {sectors.length > 0 && (
          <div className="flex items-center gap-2">
            <label className="text-xs text-[#64748b] uppercase tracking-wider">
              Sector
            </label>
            <select
              value={sectorFilter}
              onChange={(e) => setSectorFilter(e.target.value)}
              className="bg-[#1e293b] border border-[#334155] text-[#e2e8f0] text-sm rounded px-3 py-1.5 focus:outline-none focus:border-[#3b82f6]"
            >
              <option value="all">All Sectors</option>
              {sectors.map((s) => (
                <option key={s.name} value={s.name}>
                  {s.name} ({s.event_count})
                </option>
              ))}
            </select>
          </div>
        )}
        <div className="flex items-center gap-3 ml-auto">
          <span className="text-xs text-[#64748b]">
            {view === "companies"
              ? `${totalEvents} companies`
              : `${totalEvents} events · Page ${page + 1}/${totalPages || 1}`}
          </span>
          <button
            onClick={exportPDF}
            disabled={loading}
            className="px-3 py-1.5 text-xs font-medium rounded bg-[#1e293b] border border-[#334155] text-[#e2e8f0] hover:bg-[#334155] transition-colors cursor-pointer disabled:opacity-50"
          >
            Export PDF
          </button>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <LoadingState />
      ) : view === "companies" ? (
        <div className="bg-[#1e293b] border border-[#334155] rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#334155] text-[#64748b] text-xs uppercase tracking-wider">
                  <th className="text-left px-4 py-3 font-medium">Ticker</th>
                  <th className="text-left px-4 py-3 font-medium">Company</th>
                  <th className="text-left px-4 py-3 font-medium">Sector</th>
                  <th className="text-right px-4 py-3 font-medium">Events</th>
                  <th className="text-right px-4 py-3 font-medium">Max Excess</th>
                  <th className="text-right px-4 py-3 font-medium">Avg |Excess|</th>
                  <th className="text-right px-4 py-3 font-medium">Max Move</th>
                  <th className="text-left px-4 py-3 font-medium">First</th>
                  <th className="text-left px-4 py-3 font-medium">Last</th>
                </tr>
              </thead>
              <tbody>
                {companies.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-4 py-12 text-center text-[#64748b]">
                      No companies found
                    </td>
                  </tr>
                ) : (
                  companies.map((c) => (
                    <CompanyRow
                      key={c.ticker}
                      company={c}
                      onClick={() => onSelectTicker(c.ticker)}
                    />
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-[#1e293b] border border-[#334155] rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#334155] text-[#64748b] text-xs uppercase tracking-wider">
                  <th className="text-left px-4 py-3 font-medium">Ticker</th>
                  <th className="text-left px-4 py-3 font-medium">Company</th>
                  <th className="text-left px-4 py-3 font-medium">Sector</th>
                  <th className="text-left px-4 py-3 font-medium">Date</th>
                  <th className="text-right px-4 py-3 font-medium">Return</th>
                  <th className="text-right px-4 py-3 font-medium">Sector Index</th>
                  <th className="text-right px-4 py-3 font-medium">Excess</th>
                  <th className="text-center px-4 py-3 font-medium">Type</th>
                </tr>
              </thead>
              <tbody>
                {signals.length === 0 ? (
                  <tr>
                    <td
                      colSpan={8}
                      className="px-4 py-12 text-center text-[#64748b]"
                    >
                      No signals found
                    </td>
                  </tr>
                ) : (
                  signals.map((signal, idx) => (
                    <SignalRow
                      key={`${signal.ticker}-${signal.event_date}-${idx}`}
                      signal={signal}
                      onClick={() => onSelectTicker(signal.ticker)}
                    />
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
              page === 0
                ? "text-[#475569] cursor-not-allowed"
                : "text-[#e2e8f0] bg-[#1e293b] border border-[#334155] hover:bg-[#334155] cursor-pointer"
            }`}
          >
            Previous
          </button>
          <div className="flex items-center gap-1">
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                onClick={() => setPage(i)}
                className={`w-8 h-8 text-xs font-medium rounded transition-colors cursor-pointer ${
                  page === i
                    ? "bg-[#3b82f6] text-white"
                    : "text-[#94a3b8] hover:bg-[#334155]"
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
              page >= totalPages - 1
                ? "text-[#475569] cursor-not-allowed"
                : "text-[#e2e8f0] bg-[#1e293b] border border-[#334155] hover:bg-[#334155] cursor-pointer"
            }`}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, accent = false }) {
  return (
    <div className="bg-[#1e293b] border border-[#334155] rounded-lg px-5 py-4">
      <div className="text-xs text-[#64748b] uppercase tracking-wider mb-1">
        {label}
      </div>
      <div
        className={`text-2xl font-bold ${
          accent ? "text-[#f59e0b]" : "text-white"
        }`}
      >
        {value ?? "--"}
      </div>
    </div>
  );
}

function SignalRow({ signal, onClick }) {
  const returnPct = signal.daily_return_pct;
  const returnColor =
    returnPct >= 0 ? "text-[#22c55e]" : "text-[#ef4444]";
  const returnSign = returnPct >= 0 ? "+" : "";

  const mktPct = signal.market_return_pct ?? 0;
  const mktColor = mktPct >= 0 ? "text-[#22c55e]" : "text-[#ef4444]";
  const mktSign = mktPct >= 0 ? "+" : "";

  const excessPct = signal.excess_return_pct ?? returnPct;
  const excessColor = excessPct >= 0 ? "text-[#22c55e]" : "text-[#ef4444]";
  const excessSign = excessPct >= 0 ? "+" : "";

  const isCompany = signal.is_company_specific !== false;
  const idxName = signal.sector_index || "HSI";

  return (
    <tr
      onClick={onClick}
      className="border-b border-[#334155]/50 hover:bg-[#334155]/40 cursor-pointer transition-colors"
    >
      <td className="px-4 py-3">
        <span className="font-mono font-semibold text-[#3b82f6]">
          {signal.ticker}
        </span>
      </td>
      <td className="px-4 py-3 text-[#e2e8f0]">{signal.company_name}</td>
      <td className="px-4 py-3 text-[#94a3b8]">{signal.sector}</td>
      <td className="px-4 py-3 font-mono text-[#94a3b8]">
        {signal.event_date}
      </td>
      <td className={`px-4 py-3 text-right font-mono font-semibold ${returnColor}`}>
        {returnSign}
        {returnPct?.toFixed(2)}%
      </td>
      <td className={`px-4 py-3 text-right font-mono text-sm ${mktColor}`}>
        <span className="text-[#64748b] text-xs mr-1">{idxName}</span>
        {mktSign}
        {mktPct?.toFixed(2)}%
      </td>
      <td className={`px-4 py-3 text-right font-mono font-semibold ${excessColor}`}>
        {excessSign}
        {excessPct?.toFixed(2)}%
      </td>
      <td className="px-4 py-3 text-center">
        <div className="flex items-center justify-center gap-1 flex-wrap">
          <span
            className={`px-2 py-0.5 rounded text-xs font-medium ${
              isCompany
                ? "bg-[#f59e0b]/20 text-[#f59e0b]"
                : "bg-[#64748b]/20 text-[#64748b]"
            }`}
          >
            {isCompany ? "公司特有" : `跟随${idxName}`}
          </span>
          {signal.near_earnings && (
            <span className="px-2 py-0.5 rounded text-xs font-medium bg-[#8b5cf6]/20 text-[#a78bfa]" title={`财报日: ${signal.earnings_date}`}>
              财报
            </span>
          )}
        </div>
      </td>
    </tr>
  );
}

function CompanyRow({ company, onClick }) {
  const c = company;
  const excessColor = c.max_excess_pct >= 0 ? "text-[#22c55e]" : "text-[#ef4444]";
  const excessSign = c.max_excess_pct >= 0 ? "+" : "";
  const moveColor = c.max_daily_return_pct >= 0 ? "text-[#22c55e]" : "text-[#ef4444]";
  const moveSign = c.max_daily_return_pct >= 0 ? "+" : "";

  return (
    <tr
      onClick={onClick}
      className="border-b border-[#334155]/50 hover:bg-[#334155]/40 cursor-pointer transition-colors"
    >
      <td className="px-4 py-3">
        <span className="font-mono font-semibold text-[#3b82f6]">{c.ticker}</span>
      </td>
      <td className="px-4 py-3 text-[#e2e8f0]">{c.company_name}</td>
      <td className="px-4 py-3 text-[#94a3b8] text-xs">{c.sector}</td>
      <td className="px-4 py-3 text-right">
        <span className="font-mono font-bold text-[#f59e0b]">{c.total_events}</span>
      </td>
      <td className={`px-4 py-3 text-right font-mono font-semibold ${excessColor}`}>
        {excessSign}{c.max_excess_pct?.toFixed(1)}%
      </td>
      <td className="px-4 py-3 text-right font-mono text-[#94a3b8]">
        {c.avg_excess_pct?.toFixed(1)}%
      </td>
      <td className={`px-4 py-3 text-right font-mono font-semibold ${moveColor}`}>
        {moveSign}{c.max_daily_return_pct?.toFixed(1)}%
      </td>
      <td className="px-4 py-3 font-mono text-[#94a3b8] text-xs">{c.first_event}</td>
      <td className="px-4 py-3 font-mono text-[#94a3b8] text-xs">{c.last_event}</td>
    </tr>
  );
}

function LoadingState() {
  return (
    <div className="bg-[#1e293b] border border-[#334155] rounded-lg p-12 flex items-center justify-center">
      <div className="flex items-center gap-3 text-[#64748b]">
        <div className="w-4 h-4 border-2 border-[#3b82f6] border-t-transparent rounded-full animate-spin" />
        <span className="text-sm">Loading signals...</span>
      </div>
    </div>
  );
}
