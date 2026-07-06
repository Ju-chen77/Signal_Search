// In dev mode, the Vite proxy handles /api -> localhost:8000.
// For production builds or custom setups, set VITE_API_BASE_URL.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export function fetchStats(market = "us") {
  return request(`/api/stats?market=${market}`);
}

export function fetchSignals({ market = "us", limit = 50, offset = 0, sort = "recent", filter = "all", sector = "all" } = {}) {
  const params = new URLSearchParams({ market, limit, offset, sort, filter, sector });
  return request(`/api/signals?${params}`);
}

export function fetchSignalDetail(ticker, market = "us") {
  return request(`/api/signals/${encodeURIComponent(ticker)}?market=${market}`);
}

export function fetchCompanies({ market = "us", filter = "company", sort = "frequency", sector = "all" } = {}) {
  const params = new URLSearchParams({ market, filter, sort, sector });
  return request(`/api/companies?${params}`);
}

export function fetchSectors(market = "us", filter = "all") {
  const params = new URLSearchParams({ market, filter });
  return request(`/api/sectors?${params}`);
}

export function fetchBenchmark(market = "us") {
  return request(`/api/benchmark?market=${market}`);
}
