# Controversy Signal Radar

用波动率发现正在经历范式争议的公司——对标 Apple、Amazon、Tesla 等已被验证的范式公司，扫描全市场寻找类似信号。

## 它做什么

1. **建立波动率基准** — 从已知范式公司的历史数据中，找出"争议波动"的中位数强度作为门槛
2. **扫描市场** — 用门槛扫描 S&P 500（美股）或恒生指数（港股），找到所有触发信号的股票
3. **超额波动分析** — 对比恒生指数，区分「公司特有事件」和「跟随大盘」，过滤噪声
4. **新闻归因** — 为每个波动事件匹配前后的新闻，找到争议源头
5. **前端展示** — 深色主题仪表盘，支持 Events（事件列表）/ Companies（公司汇总）两种视图

## 当前数据状态

| 市场 | 数据类型 | 门槛 | 触发 | 数据源 |
|------|---------|------|------|--------|
| 美股 (US) | **演示数据** | ±10.56% | 12 只 / 14 事件 | `generate_demo.py` 生成 |
| 港股 (HK) | **真实数据** | ±14.65% | 52 只 / 333 事件（286 公司特有 + 47 跟随大盘） | akshare (东方财富) |

> 美股因 Yahoo Finance 限流暂用演示数据。待限流解除后运行 `python scripts/run_full.py --market us` 即可替换为真实数据。

## 快速开始

```bash
# 1. 克隆并安装
git clone https://github.com/Ju-chen77/Xianyi_filter.git
cd Xianyi_filter

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd frontend && npm install && cd ..

# 2. 配置（可选）
cp .env.example .env
# 填入 NEWS_API_KEY（可选，没有也能跑）

# 3. 运行数据流程
# 港股（真实数据，需关闭 VPN，约 3 分钟）
python scripts/run_full.py --market hk --skip-news

# 美股（如 Yahoo Finance 可用）
python scripts/run_full.py --market us --skip-news

# 或直接用演示数据
python scripts/generate_demo.py

# 4. 启动后端 API
uvicorn api.server:app --reload --port 8000

# 5. 启动前端（另开一个终端）
cd frontend && npm run dev

# 6. 打开浏览器访问 http://localhost:5173
```

## 分步运行

```bash
# 只计算 benchmark 基准
python scripts/run_benchmark.py --market hk

# 只扫描市场（需先跑 benchmark）
python scripts/run_scan.py --market hk

# 完整流程 + 只对波动最大的前 50 个信号做新闻归因
python scripts/run_full.py --market hk --top 50

# 跳过新闻归因（加快速度）
python scripts/run_full.py --market hk --skip-news
```

## 项目结构

```
Xianyi_filter/
├── CLAUDE.md                    # 项目核心文档（方法论+迭代计划）
├── config/
│   └── benchmarks.yaml          # Benchmark 公司名单和参数
├── src/
│   ├── data/                    # 数据获取（Yahoo Finance + akshare + 新闻）
│   ├── analysis/                # 分析引擎（基准计算 + 扫描 + 归因）
│   └── output/                  # 信号数据结构与导出
├── api/
│   └── server.py                # FastAPI 后端
├── frontend/                    # React + Tailwind 前端
├── scripts/                     # 执行脚本
├── tests/                       # 单元测试
└── data/                        # 本地数据缓存（不入 git）
```

## 当前版本

**v0.2.0** — 超额波动分析（区分公司特有事件 vs 跟随大盘）+ 港股中文公司名 + Companies 汇总视图 + 分页。

详见 [CLAUDE.md](./CLAUDE.md) 了解完整方法论和迭代计划，[CHANGELOG.md](./CHANGELOG.md) 了解版本变更记录。

## 协作

请先阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。核心约定：走分支 + PR，不直接推 main。
