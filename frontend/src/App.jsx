import { useState } from "react";
import Dashboard from "./components/Dashboard";
import StockDetail from "./components/StockDetail";
import Benchmark from "./components/Benchmark";

const PAGES = {
  DASHBOARD: "dashboard",
  DETAIL: "detail",
  BENCHMARK: "benchmark",
};

const NAV_ITEMS = [
  { key: PAGES.DASHBOARD, label: "Dashboard" },
  { key: PAGES.DETAIL, label: "Stock Detail" },
  { key: PAGES.BENCHMARK, label: "Benchmark" },
];

const MARKETS = [
  { key: "us", label: "US" },
  { key: "hk", label: "HK" },
];

export default function App() {
  const [page, setPage] = useState(PAGES.DASHBOARD);
  const [selectedTicker, setSelectedTicker] = useState(null);
  const [market, setMarket] = useState("us");

  function navigateToDetail(ticker) {
    setSelectedTicker(ticker);
    setPage(PAGES.DETAIL);
  }

  function navigateTo(key) {
    setPage(key);
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-[#e2e8f0]">
      {/* Top Navigation */}
      <nav className="bg-[#1e293b] border-b border-[#334155] sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#3b82f6] animate-pulse" />
              <span className="text-sm font-semibold tracking-wide text-[#94a3b8]">
                CSR
              </span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex gap-1">
                {NAV_ITEMS.map((item) => (
                  <button
                    key={item.key}
                    onClick={() => navigateTo(item.key)}
                    className={`px-4 py-2 text-sm font-medium rounded transition-colors cursor-pointer ${
                      page === item.key
                        ? "bg-[#3b82f6] text-white"
                        : "text-[#94a3b8] hover:text-[#e2e8f0] hover:bg-[#334155]"
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
              <div className="h-6 w-px bg-[#334155]" />
              <div className="flex gap-1">
                {MARKETS.map((m) => (
                  <button
                    key={m.key}
                    onClick={() => setMarket(m.key)}
                    className={`px-3 py-1.5 text-xs font-bold rounded transition-colors cursor-pointer ${
                      market === m.key
                        ? "bg-[#f59e0b] text-[#0f172a]"
                        : "text-[#94a3b8] hover:text-[#e2e8f0] hover:bg-[#334155] border border-[#334155]"
                    }`}
                  >
                    {m.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {page === PAGES.DASHBOARD && (
          <Dashboard onSelectTicker={navigateToDetail} market={market} />
        )}
        {page === PAGES.DETAIL && (
          <StockDetail
            ticker={selectedTicker}
            market={market}
            onBack={() => setPage(PAGES.DASHBOARD)}
          />
        )}
        {page === PAGES.BENCHMARK && <Benchmark market={market} />}
      </main>
    </div>
  );
}
