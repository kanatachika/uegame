# 《点数 / DICEBODY》（暂定代号）

> **游戏没有任何“加数值”的东西，只有能力与次数。**  
> 一款基于 **Unreal Engine 5（UE5）**、零数值成长、纯能力驱动的 **FPS 立体互坑对抗游戏**——当前已形成以「**放地图陷阱 ↔ 密闭构筑/改造 → 外环入场 FPS 对战**」为核心的三环节演进草案（v2），兼容 **1v1 宿敌局与 2~4 人开黑混战**，融合《超级鸡马》式同屏共造阴间图与《ROUNDS》式跨载体能力词条魔改。

---

## 当前项目阶段

仓库目前处于 **玩法演进验证 & 工程骨架准备期**（尚未创建 `.uproject` 引擎工程）：

- **玩法进度**：
  - **最新草案（主推验证）**：[游戏设定集（草案 v2｜方案 C：FPS 多人互坑三环节）](docs/design/游戏设定集_草案v2.md)——在 v1 零数值纯能力底座上放开限制，确立 60° 沙盘抢盒放陷阱、外环起跑带防跳关入场、胜+1/败+2 跨载体词条变形与 2 周 UE5 FPS 开黑灰盒切片。
  - **历史基线**：[游戏设定集（成品 v1）](docs/design/游戏设定集_成品v1.md)——保留 25 条原始已确认设定与 16 条历史未拍板项，供对照与追溯。
- **工程进度**：已完成目录骨架、UE5 `.gitignore` / Git LFS（含资产文件锁）、C++ 代码风格与 GitHub 自动化检查配置。待 v2 草案核心细节确认后，直接在根目录初始化 2 周 UE5 FPS 开黑灰盒（Greybox）工程即可开工。

---

## 快速导航（按需直达）

| 我想看 / 我想做 | 目录位置 | 入口文档 |
| :--- | :--- | :--- |
| 看最新的 FPS 三环节互坑方案、机关库与 2 周灰盒切片 | `docs/design/` | [游戏设定集_草案v2.md](docs/design/游戏设定集_草案v2.md) |
| 看 v1 原始 25 条已确认设定与历史待拍板基线 | `docs/design/` | [游戏设定集_成品v1.md](docs/design/游戏设定集_成品v1.md) |
| 提玩法新点子、了解分支与 PR 怎么配合 | 根目录 | [团队协作指南（CONTRIBUTING.md）](CONTRIBUTING.md) |
| 了解现在和接入 UE5 后的文件夹怎么放 | `docs/standards/` | [仓库目录结构说明](docs/standards/repo-structure.md) |
| 查蓝图、GAS 技能（`GA_`）、配表（`DT_`）、贴图怎么起名 | `docs/standards/` | [UE5 资产与代码命名规范](docs/standards/ue5-naming-conventions.md) |
| 看后续 UE5 / GAS 技术架构与同步文档（预留） | `docs/tech/` | [技术文档目录说明](docs/tech/README.md) |
| 装 Git LFS、拉大文件、给蓝图/地图加锁防冲突 | `docs/devops/` | [Git LFS 上手指南](docs/devops/git-lfs-guide.md) |
| 看 GitHub 自动门卫检查什么、亮红灯怎么修 | `docs/devops/` | [CI/CD 自动检查说明](docs/devops/ci-cd-overview.md) |

---

## 仓库目录概览

```text
uegame/
├── .github/                  # GitHub Actions 自动检查、Issue 创意/决策表单、PR 模板、CODEOWNERS
├── docs/
│   ├── design/               # 游戏玩法设定集与后续配表/关卡设计草案
│   ├── standards/            # 仓库目录规范、UE5 资产与 C++/GAS 命名规范
│   ├── tech/                 # UE5 技术方案与核心模块实现文档（随开发补充）
│   └── devops/               # Git LFS 使用教程、CI 自动检查与构建说明
├── .clang-format             # UE5 C++ 代码格式化规则（Allman 大括号、保护 .generated.h）
├── .editorconfig             # 跨编辑器编码（UTF-8）与缩进规则
├── .gitattributes            # Git LFS 二进制资产跟踪、.uasset/.umap 文件锁、统一换行符
├── .gitignore                # UE5 本地编译产物与 IDE 缓存忽略规则
├── CONTRIBUTING.md           # 面向策划与程序的日常协作流程
└── README.md                 # 当前页面
```

> **后续 UE5 工程放哪？**  
> 开始搭原型时，直接在仓库根目录放置 `Dicebody.uproject`（及 `Config/`、`Source/`、`Content/`、`Plugins/`）。完整的 UE5 目录规划请看 [仓库目录结构说明](docs/standards/repo-structure.md)。

---

## 新队友 3 分钟上手

### 如果你主要聊玩法、提创意（不用敲命令行）

1. 先读 [游戏设定集_草案v2.md](docs/design/游戏设定集_草案v2.md) 了解最新的 FPS 三环节互坑方案（含 v1→v2 迁移对照与 2 周灰盒验证目标），如需追溯原始基线可对照 [游戏设定集_成品v1.md](docs/design/游戏设定集_成品v1.md)。
2. 有新点子或想拍板某个待定问题，直接在 GitHub 网页顶部点 **Issues → New issue**，选对应的模板填好发出来就行，具体说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 如果你要拉取仓库、写文档或准备开发

1. **先装好 Git 和 Git LFS**（只需在自己电脑上初始化一次，详细步骤见 [Git LFS 上手指南](docs/devops/git-lfs-guide.md)）：
   ```powershell
   git lfs install
   ```
2. **克隆仓库到本地**：
   ```powershell
   git clone https://github.com/kanatachika/uegame.git
   cd uegame
   ```
3. **动手改东西前**：瞄一眼 [CONTRIBUTING.md](CONTRIBUTING.md)，拉个自己的小分支再改，别直接往 `main` 分支硬推。
