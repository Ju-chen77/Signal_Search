# CLAUDE.md — 争议信号雷达 (Controversy Signal Radar)

> 本文件是项目核心文档。所有协作者和AI在动手前先读完这个文件。
> 项目采用迭代开发，从最小可用功能开始，逐版叠加。

---

## 一、我们在做什么

我们是一家金融公司的初创团队（三人小组，GitHub协作）。

我们相信：**真正的范式公司（下一个亚马逊、下一个苹果）在成长过程中一定伴随巨大争议，这些争议会体现在股价的异常波动上。** 我们要做的是一个"争议信号雷达"——用波动率作为第一个筛子，从公开市场中自动发现那些正在经历争议的公司，然后人工深入研究。

核心逻辑链：
1. 用已知的范式公司建立"争议波动率"的基准线
2. 拿这个基准线去扫描全市场
3. 找到触发信号的股票，并归因每次波动（找到对应的新闻/事件）
4. 前端展示，团队每天打开就能看到新信号

**当前版本（v0.1）只做美股，数据源用Yahoo Finance。** 跑通后再扩展到港股和A股。

---

## 二、Benchmark公司名单

这些公司都是已知的"范式公司"——在成长过程中经历了巨大争议和股价剧烈波动，最终证明了自己。

### 美股（无涨跌停限制）
| 公司 | Ticker | 争议本质 |
|------|--------|---------|
| 苹果 | AAPL | 电脑公司→消费电子→服务平台，2000年单日暴跌51% |
| 亚马逊 | AMZN | 网上书店→万物商店→云计算，2000年跌94%，分析师目标价差8倍 |
| 特斯拉 | TSLA | 汽车公司→科技公司→能源→AI机器人，做空之王，2020年涨740%后2022年跌65% |
| Netflix | NFLX | DVD邮寄→流媒体→内容制作，2011年跌80%，2022年又跌75% |
| Nvidia | NVDA | 游戏显卡→AI基础设施，估值框架被彻底改写 |
| Meta | META | 社交网络→元宇宙→AI，2022年跌75%后2023年涨200% |

### 港股（无涨跌停限制，v0.2实现）
| 公司 | Ticker | 争议本质 |
|------|--------|---------|
| 泡泡玛特 | 9992.HK | 玩具厂→IP平台→中国迪士尼？两次经历90%级别回撤 |
| 小米 | 1810.HK | 手机公司→IoT平台→造车，上市即破发到翻倍再到造车争议 |
| 比亚迪 | 1211.HK | 电池制造→电动车→全球新能源出口商 |
| 美团 | 3690.HK | 外卖→本地生活→社区团购，反垄断暴跌后恢复 |

### A股（10%/20%涨跌停限制，v0.3实现）
| 公司 | Ticker | 争议本质 |
|------|--------|---------|
| 寒武纪 | 688256.SH | 讲故事还是真赚钱？PE 369倍 vs 行业75倍，营收预测差2.5倍 |
| 宁德时代 | 300750.SZ | 制造业还是科技公司？万亿市值后产能过剩恐慌 |
| 科大讯飞 | 002230.SZ | 每波AI热潮都炒一波，然后被质疑"有没有真AI能力" |

---

## 三、核心方法论

### Step 1：建立波动率基准

拉取每个benchmark公司**过去5年**的日线数据，识别所有"大波动事件"。

大波动事件的定义（v0.1先用单日维度）：
- 单日涨跌幅绝对值超过一定阈值的交易日
- 从benchmark公司的所有大波动事件中，取**中位数**作为门槛

为什么取中位数：最初用最小值，导致港股 94% 的股票都触发了，没有区分度。中位数代表"典型的争议波动强度"，既不会太宽松也不会太严格，各市场通用。

**不同市场要分别建基准**（因为涨跌停规则不同）：
- 美股基准：从AAPL/AMZN/TSLA/NFLX/NVDA/META的数据中得出
- 港股基准：从9992.HK/1810.HK/1211.HK/3690.HK的数据中得出（v0.2）
- A股基准：从688256.SH/300750.SZ/002230.SZ的数据中得出（v0.3）

### Step 2：扫描全市场

用基准门槛扫描目标市场的所有股票（v0.1先做美股）：
- 拉取全美股过去5年的日线数据
- 找出每只股票触发门槛的所有日期
- 记录：股票代码、触发日期、当日涨跌幅、成交量变化

### Step 3：波动归因

对每个触发事件，自动查找对应日期前后的新闻：
- 用新闻API或搜索引擎查找该股票在波动日前后1-2天的新闻
- 提取新闻标题和摘要
- 这就是"波动源头"——争议的具体内容

### Step 4：前端展示

一个网页，打开就能看到：
- 哪些股票最近触发了争议波动信号
- 每个信号对应的波动幅度和新闻归因
- 可以按时间、幅度、行业筛选

---

## 四、技术架构

```
xfactor-radar/
├── CLAUDE.md                    # 本文件
├── README.md                    # GitHub仓库说明
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量模板（API keys等）
├── .gitignore
│
├── config/
│   └── benchmarks.yaml          # Benchmark公司名单和配置
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/                    # 数据获取
│   │   ├── __init__.py
│   │   ├── yahoo_client.py      # Yahoo Finance数据拉取
│   │   └── news_client.py       # 新闻数据获取（归因用）
│   │
│   ├── analysis/                # 分析引擎
│   │   ├── __init__.py
│   │   ├── benchmark.py         # 从benchmark公司计算波动率基准
│   │   ├── scanner.py           # 用基准扫描全市场
│   │   └── attribution.py       # 波动事件归因（匹配新闻）
│   │
│   └── output/                  # 结果输出
│       ├── __init__.py
│       └── signals.py           # 信号数据结构和导出
│
├── frontend/                    # 前端（React）
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx              # 主页面
│   │   ├── components/
│   │   │   ├── SignalList.jsx    # 信号列表
│   │   │   ├── SignalCard.jsx    # 单个信号卡片
│   │   │   ├── StockDetail.jsx   # 股票详情页
│   │   │   └── Filters.jsx      # 筛选器
│   │   └── utils/
│   │       └── api.js           # 前端调后端的接口
│   └── public/
│
├── api/                         # 后端API（给前端提供数据）
│   ├── __init__.py
│   └── server.py                # FastAPI或Flask服务
│
├── scripts/
│   ├── run_benchmark.py         # 计算benchmark基准
│   ├── run_scan.py              # 扫描全市场
│   └── run_full.py              # 完整流程：基准→扫描→归因→输出
│
├── data/                        # 本地数据缓存（不提交git）
│   ├── prices/                  # 股价数据缓存
│   ├── signals/                 # 扫描结果
│   └── news/                    # 新闻归因缓存
│
└── tests/
    ├── test_benchmark.py
    ├── test_scanner.py
    └── test_attribution.py
```

### 技术栈

- **后端**：Python 3.11+
- **股价数据**：yfinance（Yahoo Finance的Python库）
- **新闻数据**：Google News RSS / NewsAPI（免费层）/ Yahoo Finance自带新闻
- **后端API**：FastAPI
- **前端**：React + Tailwind CSS
- **数据存储**：v0.1用JSON文件存本地，后续再上数据库

---

## 五、v0.1 具体范围

**只做美股。只做波动率筛选 + 新闻归因。先跑通再说。**

功能清单：
- [x] 拉取6家美股benchmark公司过去5年日线数据
- [x] 计算波动率基准（取大波动事件中最小的）
- [x] 扫描美股市场（先从S&P 500或Russell 1000开始，不用全市场）
- [x] 对触发信号的股票，抓取对应日期的新闻
- [x] 前端页面展示信号列表
- [x] 点击可看详情（波动图 + 新闻归因）

不做的：
- 不做港股/A股（v0.2/v0.3）
- 不做实时更新（v0.1是静态扫描，跑一次看结果）
- 不做AI分析或打分
- 不做用户登录或权限

---

## 六、迭代计划

### v0.1 — 跑通最小闭环（当前）
美股波动率筛选 + 新闻归因 + 前端展示

### v0.2 — 扩展市场
加入港股benchmark和扫描（需要处理港股数据源）

### v0.3 — A股
加入A股benchmark和扫描（需要处理涨跌停板逻辑，波动率基准计算方式不同）

### v0.4 — 实时化
每日自动更新，打开网站就能看到今天是否有新信号

### v0.5 — 深度分析
基于v0.1-v0.4积累的数据，找触发信号公司的共同点
加入第二个筛子（比如分析师分歧、估值框架矛盾等）

---

## 七、开发约定

- Python代码写类型注解
- 所有配置走config文件或环境变量
- data/目录在.gitignore中，不提交原始数据
- API密钥走.env文件
- commit message格式：`[模块] 简要描述`
- main分支保持可运行
- 以项目负责人思路为准，有问题先讨论再改

---

## 八、关键设计决策备忘

1. **波动率基准取"大波动的中位数"**：v0.1 用最小值导致港股 94% 触发、毫无区分度，改为中位数后含义是"典型争议波动的强度"，各市场通用
2. **五年窗口**：一个商业模式的变化五年内一定能看到
3. **不同市场不同基准**：美股无涨跌停可以单日跌50%，A股最多20%，不能混用
4. **新闻归因是为了让人看懂**：系统只负责找到波动和对应新闻，判断交给人
5. **先做美股**：Yahoo Finance数据最好拿，英文新闻最好找

---

## 九、AI 协作开发规范

> **所有使用 AI（Claude Code / Cursor / Copilot 等）参与本项目开发的人，必须遵守以下规范。**
> 这套规则让任何人（或 AI）拿到仓库后，都能理解怎么迭代、改什么、加什么、才能跑通。

### 9.1 版本命名规则

```
v{大版本}.{小版本}.{补丁}
```

| 位 | 何时递增 | 示例 |
|---|---------|------|
| 大版本 | 新增一个完整市场或重大架构变更 | v1.0（上线生产） |
| 小版本 | 新增一个功能模块（如港股扫描、实时更新） | v0.2（加港股） |
| 补丁 | Bug 修复、小调整、文档更新 | v0.1.1 |

当前版本对照表：

| 版本 | 内容 | 状态 |
|------|------|------|
| v0.1.0 | 美股波动率筛选 + 新闻归因 + 前端展示 | **已完成**（美股为演示数据） |
| v0.1.1 | 港股真实数据 + 门槛从最小值改为中位数 | **已完成** |
| v0.2.0 | 超额波动分析（区分公司特有 vs 跟随大盘）+ 港股公司名 | **已完成** |
| v0.3.0 | 加 A 股 benchmark + 涨跌停逻辑 | 待开发 |
| v0.4.0 | 每日自动更新（定时任务） | 待开发 |
| v0.5.0 | 深度分析（AI 验证业态变化） | 待开发 |

### 9.2 每次迭代必须做的事

**开发前（准备）：**

1. 从 `main` 拉新分支，命名格式：`feat/v0.x-简要描述`
2. 读完本文件（CLAUDE.md）和 `CHANGELOG.md`，了解当前版本和已有功能
3. 确认你要做的版本范围，不要越界

**开发中（代码）：**

4. **每个新版本至少更新以下文件：**

| 文件 | 做什么 |
|------|--------|
| `config/benchmarks.yaml` | 如果新增市场/benchmark公司，在这里加配置 |
| `src/` 下对应模块 | 新增或修改 Python 代码 |
| `frontend/src/` | 如果前端需要展示新内容，改对应组件 |
| `api/server.py` | 如果新增了 API 端点 |
| `tests/` | **必须**为新功能写测试，跑通后再提 PR |
| `requirements.txt` | 如果引入了新的 Python 包 |
| `frontend/package.json` | 如果引入了新的 npm 包 |

5. 跑通检查清单（**全部通过才能提 PR**）：

```bash
# Python 测试
python -m pytest tests/ -v

# 导入检查（不报错就行）
python -c "from src.analysis.benchmark import calculate_benchmark; print('OK')"

# FastAPI 能启动
uvicorn api.server:app --port 8000 &
curl http://localhost:8000/api/stats
kill %1

# 前端能编译
cd frontend && npm run build && cd ..
```

**开发后（记录）：**

6. 更新 `CHANGELOG.md`，在最上面加新版本的记录
7. 更新本文件（CLAUDE.md）第五节"当前版本范围"和第六节"迭代计划"中对应版本的状态
8. 提 PR，标题格式：`feat: v0.x — 简要描述`

### 9.3 各版本的具体开发指引

#### v0.2（港股）要做什么

需要新增/修改的文件：

```
config/benchmarks.yaml          → hk.scan_universe 从 null 改为实际值
src/data/yahoo_client.py        → 确认 yfinance 能拉港股数据（.HK 后缀）
                                  如果不行，新增港股数据源模块
src/analysis/benchmark.py       → calculate_benchmark("hk") 应能正常工作（已支持，需验证）
src/analysis/scanner.py         → scan_market("hk", ...) 需要实现港股股票列表获取
                                  新增 get_hk_tickers() 函数
frontend/src/components/*.jsx   → 前端加市场切换下拉框（US / HK）
frontend/src/utils/api.js       → API 调用加 market 参数（已支持）
api/server.py                   → 端点已支持 market 参数，无需改动
tests/                          → 新增 test_hk_benchmark.py 或在现有测试中加港股用例
CHANGELOG.md                    → 记录 v0.2 变更
```

#### v0.3（A 股）要做什么

```
config/benchmarks.yaml          → a_share.scan_universe 设为实际值
src/data/                       → 可能需要新数据源（yfinance 对 A 股支持有限）
                                  如果用 akshare/tushare，需加到 requirements.txt
src/analysis/benchmark.py       → A 股有涨跌停，波动率计算需要考虑
                                  has_price_limit=true 时的处理逻辑
src/analysis/scanner.py         → get_ashare_tickers() 获取 A 股列表
                                  涨跌停日的信号是否有效需要判断
tests/                          → A 股相关测试
CHANGELOG.md                    → 记录 v0.3 变更
```

#### v0.4（实时化）要做什么

```
scripts/                        → 新增 run_daily.py（每日定时跑的脚本）
src/analysis/scanner.py         → 增量扫描逻辑（只拉最近N天，不重新拉5年）
api/server.py                   → 可能加 WebSocket 推送新信号
frontend/                       → 加"最后更新时间"显示、自动刷新
部署相关                         → Dockerfile / cron 配置 / 云服务器部署文档
CHANGELOG.md                    → 记录 v0.4 变更
```

### 9.4 代码规范（AI 必读）

1. **Python 写类型注解**：函数参数和返回值必须标注类型
2. **不要硬编码**：所有阈值、公司列表、参数走 `config/benchmarks.yaml` 或 `.env`
3. **数据获取必须有**：缓存 + 限流（sleep）+ 失败重试（最多3次）+ 单票失败不中断整体
4. **新闻归因是尽力而为**：找不到新闻标记 `attributed: false`，不要报错或中断
5. **JSON 文件做数据存储**：v0.1-v0.3 都不用数据库，数据存 `data/` 目录
6. **`data/` 目录不入 git**：所有运行时数据、缓存都在这里，`.gitignore` 已排除
7. **不要删除或重写已有且能工作的代码**，除非你确认它有 bug 或需求变了
8. **不要编造不存在的 API 或库**：如果不确定某个库是否支持某功能，先测试再写

### 9.5 文件职责速查（不要放错位置）

| 你要做的事 | 该改的文件 |
|-----------|-----------|
| 加新的 benchmark 公司 | `config/benchmarks.yaml` |
| 加新的数据源（比如 akshare） | `src/data/` 下新建模块，`requirements.txt` 加依赖 |
| 改波动率计算方式 | `src/analysis/benchmark.py` |
| 改扫描范围或逻辑 | `src/analysis/scanner.py` |
| 改新闻归因逻辑 | `src/analysis/attribution.py` |
| 加新的 API 端点 | `api/server.py` |
| 改前端页面 | `frontend/src/components/` |
| 改前端调后端的方式 | `frontend/src/utils/api.js` |
| 加执行脚本 | `scripts/` |
| 改配置参数 | `config/benchmarks.yaml` 或 `.env.example` |

### 9.6 Git 分支和提交规范

**分支命名：**
```
feat/v0.2-hk-market       # 新功能
fix/scanner-timeout        # 修 bug
docs/update-changelog      # 文档
refactor/data-layer        # 重构
```

**Commit message 格式：**
```
feat: 添加港股 benchmark 计算
fix: 修复 scanner 超时后不重试的问题
docs: 更新 CHANGELOG v0.2
test: 添加港股扫描测试用例
refactor: 统一数据源接口
```

**PR 规则：**
- 标题：`feat: v0.x — 简要描述`
- 描述中列出：改了什么、为什么改、怎么测试
- 必须所有测试通过
- 至少一人 review
