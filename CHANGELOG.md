# Changelog

本文件记录每个版本的主要变更。格式参考 [Keep a Changelog](https://keepachangelog.com/)。

---

## [v0.2.0] - 2026-07-06

### 概述

新增「超额波动」分析——区分公司特有事件和跟随大盘。**这是第二层筛选：第一层用绝对波动率找到候选，第二层用超额波动排除大盘拖累，留下真正值得人工调查的信号。**

### 完整判断流程

```
全市场所有股票（恒生指数 72 只）
    ↓ 第一筛：单日涨跌幅 > ±14.65%（benchmark 中位数）
333 个事件（52 只股票）
    ↓ 第二筛：超额波动 = 个股涨跌 - 恒生指数涨跌
    ↓ 标记：|超额波动| > |大盘波动| → 「公司特有」，否则 → 「跟随大盘」
公司特有事件（值得人工深入调查）
    ↓ 人工验证
判断是否为范式转变信号 → 反馈 → 优化筛选逻辑
```

### 新增

- `download_hsi_index()` — 获取恒生指数过去5年日线数据，用于计算超额波动
- `Signal` / `AttributedSignal` 新增字段：`market_return_pct`（大盘涨跌）、`excess_return_pct`（超额波动）、`is_company_specific`（是否公司特有事件）
- Scanner 扫描完成后自动计算每个事件的超额波动
- API 新增 `filter` 参数：`all` / `company` / `market`，可只看公司特有事件
- 前端信号表格新增「超额波动」列 + 公司/大盘标签 + 筛选按钮
- 港股公司名补全（中文名，新浪数据源）
- **Companies 汇总视图** — 每家公司一行，显示触发次数、最大/平均超额波动、时间跨度
- `/api/companies` 端点 — 公司级汇总数据，支持按频率/最大超额/平均超额/时间排序
- 前端 Events / Companies 视图切换
- 信号列表分页（每页50条，底部翻页按钮）
- **Export PDF** — 导出当前视图为 PDF（浏览器原生打印，完美支持中文）

### 变更

- `scanner.py` — 扫描后额外拉取 HSI 指数数据，计算超额波动
- `signals.py` — 数据结构扩展，兼容旧数据（新字段有默认值）
- `api/server.py` — 信号端点支持 `filter` 查询参数，新增 `/api/companies` 端点
- `Dashboard.jsx` — 新增超额波动列、事件类型标签、筛选控件、Companies 视图、分页
- `akshare_client.py` — 公司名数据源从 `stock_hk_spot_em()`（东方财富，太慢超时）改为 `stock_hk_spot()`（新浪，秒级返回）

---

## [v0.1.1] - 2026-07-06

### 概述

港股扫描上线 + benchmark 门槛优化。**美股数据为演示数据（Yahoo Finance 限流未解除），港股为真实数据。**

### 新增

- `src/data/akshare_client.py` — 港股数据源（akshare / 东方财富），解决 Yahoo Finance 限流问题
- `get_hsi_tickers()` — 恒生指数 72 只成分股列表（内置 + Wikipedia 抓取兜底）
- 前端导航栏 US / HK 市场切换按钮
- 所有 API 端点和前端组件支持 `market` 参数

### 变更

- **benchmark 门槛算法**：从"所有显著波动事件中取最小值"改为"取中位数"
  - 原因：最小值导致港股 94% 的股票都触发信号（68/72），完全没有区分度
  - 效果：港股 68→52 只触发，美股 22→12 只触发
- `config/benchmarks.yaml` — 港股 `scan_universe` 从 `null` 改为 `"hsi"`
- `scanner.py` — 支持 `market="hk"` 分支，港股走 akshare 数据源
- `benchmark.py` — 港股走 `batch_download_hk()`
- `requirements.txt` — 新增 `akshare>=1.14`

### 当前数据状态

| 市场 | 数据类型 | 门槛 | 触发 | 事件数 |
|------|---------|------|------|--------|
| 美股 (US) | **演示数据** | ±10.56% | 12 只 | 14 个 |
| 港股 (HK) | **真实数据** | ±14.65% | 52/72 只 | 333 个 |

> 美股数据来源：`scripts/generate_demo.py` 生成的模拟数据。待 Yahoo Finance 限流解除后，运行 `python scripts/run_full.py --market us --skip-news` 替换为真实数据。

---

## [v0.1.0] - 2026-07-06

### 概述

首个可运行版本——跑通"波动率基准 → 全市场扫描 → 新闻归因 → 前端展示"的完整链路。

### 新增

**后端 Python**
- `config/benchmarks.yaml` — Benchmark 公司名单及参数配置（美股/港股/A股，后两者为预留）
- `src/output/signals.py` — 核心数据结构（BenchmarkEvent, BenchmarkResult, Signal, NewsItem, AttributedSignal, ScanResult），支持 JSON 持久化
- `src/data/yahoo_client.py` — yfinance 数据拉取，带本地缓存（`data/prices/`）、限流（0.5s）、失败重试（3次）
- `src/data/news_client.py` — 三源新闻获取（Yahoo Finance / Google News RSS / NewsAPI），带缓存和去重
- `src/analysis/benchmark.py` — 波动率基准计算：第99百分位显著波动 → 取中位数作为门槛
- `src/analysis/scanner.py` — S&P 500 / 恒生指数全市场扫描，单票失败不中断整体
- `src/analysis/attribution.py` — 为每个波动事件匹配新闻进行归因
- `api/server.py` — FastAPI 后端，4 个 API 端点（benchmark / signals / signals/{ticker} / stats），CORS 已开
- `scripts/run_benchmark.py` — 单独计算 benchmark 基准
- `scripts/run_scan.py` — 单独扫描市场
- `scripts/run_full.py` — 完整流程（benchmark → scan → attribution），支持 `--skip-news` 和 `--top N` 参数
- `scripts/generate_demo.py` — 生成美股演示数据

**前端 React**
- Vite + React + Tailwind CSS，深色主题（Bloomberg Terminal 风格）
- Dashboard 页面：信号列表表格，支持按时间/幅度/频率排序，按行业筛选
- StockDetail 页面：股价走势图（recharts）+ 事件时间线 + 新闻归因
- Benchmark 页面：门槛计算说明 + benchmark 公司汇总卡片
- US / HK 市场切换

**测试**
- 12 个单元测试覆盖 benchmark 计算、scanner 扫描、attribution 归因的核心逻辑

**文档**
- `CLAUDE.md` — 项目核心文档（方法论 + 迭代计划 + AI 协作规范）
- `README.md` — 快速启动指南
- `CONTRIBUTING.md` — 协作规范
- `docs/SETUP.md` — 详细安装指南
- `CHANGELOG.md` — 本文件

### 技术栈

| 组件 | 技术 | 版本要求 |
|------|------|---------|
| 后端语言 | Python | 3.10+ |
| 股价数据 | yfinance / akshare | ≥0.2.31 / ≥1.14 |
| 数据处理 | pandas, numpy | ≥2.0, ≥1.24 |
| 后端 API | FastAPI + Uvicorn | ≥0.104 |
| 新闻数据 | feedparser, requests | ≥6.0, ≥2.31 |
| 前端框架 | React (Vite) | 19.x |
| 前端样式 | Tailwind CSS | 4.x |
| 前端图表 | recharts | 2.x |
| 运行时 | Node.js | 18+ |

### 不做的（留给后续版本）

- A股扫描（v0.3）
- 实时更新（v0.4）
- AI 分析或打分（v0.5）
- 用户登录或权限
- 数据库（当前用 JSON 文件）

---

## 迭代计划

| 版本 | 目标 | 状态 |
|------|------|------|
| v0.1 | 美股波动率筛选 + 前端展示 | **已完成**（演示数据） |
| v0.1.1 | 港股真实数据 + 门槛优化 | **已完成** |
| v0.2 | 美股真实数据 + 港股公司名 | 待开发 |
| v0.3 | 加入 A 股（涨跌停板逻辑）| 待开发 |
| v0.4 | 每日自动更新 | 待开发 |
| v0.5 | 深度分析（第二个筛子）| 待开发 |
