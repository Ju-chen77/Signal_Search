# 环境搭建指南

## 前置条件

你需要安装以下软件。如果已有可跳过。

### 1. Python 3.10+

检查是否已安装：
```bash
python3 --version
```

如未安装（macOS）：
```bash
brew install python@3.13
```

### 2. Node.js 18+

检查是否已安装：
```bash
node --version
npm --version
```

如未安装（macOS 推荐用 nvm）：
```bash
# 安装 nvm（Node 版本管理器）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 重新打开终端后
nvm install 22
nvm use 22
```

或直接用 Homebrew：
```bash
brew install node
```

### 3. Git

```bash
git --version    # macOS 自带
```

---

## 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Ju-chen77/Xianyi_filter.git
cd Xianyi_filter

# 2. 创建 Python 虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. 安装前端依赖
cd frontend
npm install
cd ..

# 4.（可选）配置环境变量
cp .env.example .env
# 编辑 .env，填入 NEWS_API_KEY（可选，没有也能跑）
```

---

## 运行

### 完整数据流程

```bash
# 激活虚拟环境（如果还没激活）
source .venv/bin/activate

# --- 港股（真实数据，推荐先跑这个） ---
# ⚠️ 需要关闭 VPN（akshare 数据源在国内）
# 首次约 3-5 分钟，数据会缓存到 data/prices/
python scripts/run_full.py --market hk --skip-news

# --- 美股（Yahoo Finance 可能限流） ---
# 首次需要 30-60 分钟拉取 500 只股票数据
python scripts/run_full.py --market us

# --- 或者直接用演示数据（秒级生成） ---
python scripts/generate_demo.py

# 加快速度的选项：
python scripts/run_full.py --market hk --skip-news          # 跳过新闻归因
python scripts/run_full.py --market hk --top 50             # 只对前50个信号做新闻归因
```

### 启动服务

需要两个终端窗口：

**终端 1 — 后端 API：**
```bash
source .venv/bin/activate
uvicorn api.server:app --reload --port 8000
```

**终端 2 — 前端：**
```bash
cd frontend
npm run dev
```

打开浏览器访问 http://localhost:5173

### 分步运行

```bash
python scripts/run_benchmark.py --market us     # 只计算 benchmark 基准
python scripts/run_scan.py --market us           # 只扫描市场（需先跑 benchmark）
```

---

## 运行测试

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

---

## 常见问题

**Q: yfinance 拉取数据很慢？**
A: 正常。首次运行需要拉取 500+ 只股票各 5 年的日线数据。数据会缓存到 `data/prices/`，之后再跑同一天不会重复拉取。

**Q: 港股数据跑不出来？**
A: 港股数据通过 akshare（新浪数据源）获取，需要**关闭 VPN**。如果开着科学上网会连不上国内数据源。

**Q: 报错 "Benchmark 数据不存在"？**
A: 需要先运行 `python scripts/run_full.py --market hk` 或 `--market us` 生成数据，API 才能提供数据给前端。也可以用 `python scripts/generate_demo.py` 快速生成美股演示数据。

**Q: 没有 NEWS_API_KEY 能跑吗？**
A: 能。新闻归因会用 Yahoo Finance 和 Google News RSS 两个免费源。NewsAPI 只是可选补充。

**Q: 前端打开是空白？**
A: 检查后端 API 是否在运行（端口 8000），以及是否已运行过数据流程生成了 `data/signals/` 下的 JSON 文件。
