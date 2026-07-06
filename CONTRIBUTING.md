# 协作规范（CONTRIBUTING）

本项目多人协作，请所有人遵守以下流程，避免代码冲突和误操作。

## 一、分支策略

- `main`：稳定分支，**不允许直接 push**，只能通过 Pull Request 合并。
- 功能分支：每个人开发新功能时，从最新的 `main` 拉一个分支。

分支命名：`类型/简短描述`，例如：

```
feat/v0.3-a-share            # 新功能（A股扫描）
fix/scanner-timeout          # 修 bug
docs/update-changelog        # 文档更新
refactor/data-layer          # 重构
```

## 二、日常开发流程

```bash
# 1. 每次开工前，先同步最新 main
git checkout main
git pull

# 2. 从 main 拉自己的功能分支
git checkout -b feat/你的功能

# 3. 开发 + 提交（小步提交，信息清晰）
git add .
git commit -m "feat: 添加港股超额波动分析"

# 4. 推送分支到远程
git push -u origin feat/你的功能

# 5. 到 GitHub 上开 Pull Request，指派同事 review
# 6. review 通过后合并到 main，删除功能分支
```

## 三、Commit 信息规范

格式：`类型: 简短标题`，常用类型：

| 前缀 | 含义 |
|---|---|
| `feat:` | 新功能 |
| `fix:` | 修 bug |
| `refactor:` | 重构 |
| `data:` | 数据/抓取来源相关 |
| `docs:` | 文档 |
| `test:` | 测试 |
| `wip:` | 未完成，临时保存 |

## 四、绝对不要提交的东西

- `.env`（含 API key、账号密码）——已在 `.gitignore`
- `data/`（股价缓存、信号结果、新闻缓存）——已在 `.gitignore`
- 任何个人账号、Cookie、token

> 提交前先跑 `git status` 确认没有把敏感文件加进去。

## 五、代码约定

- 每个函数写清楚：输入参数、返回值、功能描述。
- 抓取代码必须加 `try/except` + 重试 + `sleep`（防封 IP）。
- 配置项（阈值、benchmark 名单、来源开关）统一写在 `config/benchmarks.yaml`，不要硬编码。
- 不确定的地方写 `# TODO: 说明`，不要乱猜。

## 六、建议在 GitHub 上开启分支保护

仓库 owner 可在 **Settings → Branches → Add branch ruleset** 中对 `main` 开启：
- Require a pull request before merging（合并前必须 PR）
- Require approvals（至少 1 人 review 通过）

这样能防止有人误操作直接推到 `main`。
