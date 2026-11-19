# 仓库目录结构说明

这篇文档把仓库里每个文件夹是干嘛的说清楚——包括**现在仓库里有什么**，以及**等开始搭 UE5 工程之后，代码和资产往哪放**。

---

## 1. 为什么现在还没有 `.uproject`？

目前《点数 / DICEBODY》还在**玩法打磨与拍板阶段**（见 [设定集 v1](../design/模块化FPS_设定集_整合版v1.md) 第 8 章的 7 个 `P0` 待定问题，比如部位怎么挂模块、空部位受击怎么算、一局几条命等）。

过早建 UE5 工程很容易出现“规则一改，底层角色类和碰撞盒全推倒重来”的情况。所以我们先把文档归档、Git LFS 大文件规则、命名约定和自动检查搭好；等 `P0` 问题拍板后，直接在当前仓库根目录接入干净的 UE5 灰盒工程。

---

## 2. 当前阶段的目录布局

```text
uegame/
├── .github/                        # GitHub 自动化配置（自动检查流水线、Issue/PR 模板、负责人）
├── docs/                           # 项目所有文档集中地
│   ├── design/                     # 玩法设定集、数值草稿、关卡设计文档
│   │   └── 模块化FPS_设定集_整合版v1.md
│   ├── standards/                  # 团队协作与 UE5 工程规范（你正在看这里）
│   │   ├── repo-structure.md       # 仓库目录结构说明
│   │   └── ue5-naming-conventions.md # UE5 资产与 C++/GAS 命名规范
│   ├── tech/                       # 后续 UE5 技术方案与模块架构文档
│   │   └── README.md
│   └── devops/                     # Git LFS 操作手册与自动检查说明
│       ├── git-lfs-guide.md
│       └── ci-cd-overview.md
├── .clang-format                   # UE5 C++ 代码自动格式化配置
├── .editorconfig                   # 编辑器缩进、编码与换行符统一配置
├── .gitattributes                  # Git LFS 大文件跟踪、文件锁与换行符规则
├── .gitignore                      # UE5 编译缓存与本地临时文件忽略规则
├── CONTRIBUTING.md                 # 队友日常协作指南（提想法、拉分支、发 PR）
└── README.md                       # 仓库首页总览与快速入口
```

---

## 3. 接入 UE5 工程后的完整布局

等开工建工程时，请直接在**仓库根目录**创建 `.uproject`（暂定名 `Dicebody.uproject`，正式定名后按英文名命名，不要带中文或空格）。接入后的完整目录如下：

```text
uegame/
├── Dicebody.uproject               # [入库] UE5 工程入口文件
├── Config/                         # [入库] 引擎、输入、网络、GameplayTags 等 .ini 配置
├── Source/                         # [入库] C++ 源代码与构建脚本（*.Build.cs / *.Target.cs）
│   ├── Dicebody/                   # 主游戏模块（Pawn、GAS 技能、部位耐久、对局状态）
│   └── DicebodyEditor/             # 编辑器辅助工具模块（按需添加）
├── Content/                        # [入库 · 走 Git LFS + 文件锁] 引擎内所有游戏资产
│   ├── Dicebody/                   # 本项目正式资产统一收口在主目录下，方便和商城素材区分
│   │   ├── Core/                   # GameMode、GameState、PlayerController、基础白板 Pawn
│   │   ├── Abilities/              # GAS 能力模块（GA_ 跑/跳/爬/滑铲、GE_ 耐久与点数、GC_ 表现）
│   │   ├── Weapons/                # 保底手枪、正式武器与弹道表现
│   │   ├── Data/                   # 配表（DT_ 模块定价表、合成配方表、DA_ 模块定义卡）
│   │   ├── Maps/                   # 关卡地图（L_ 灰盒测试场、正式 1v1 对战图）
│   │   ├── UI/                     # 界面（WBP_ 身体部位耐久面板、选配/合成轮盘、掷骰界面）
│   │   ├── Characters/             # 角色骨骼网格体、碰撞盒与动画蓝图
│   │   ├── Environment/            # 场景模型、高台/矮缝灰盒白模、材质与贴图
│   │   ├── VFX/                    # Niagara 粒子特效（部位受损火花、据点光圈等）
│   │   └── Audio/                  # 音效（脚步声、跳跃落点声、部位打坏提示音）
│   └── Developers/                 # 个人实验沙盒（Content/Developers/<你的英文名>/）
├── Plugins/                        # [入库] 项目自研插件或轻量第三方插件（插件内 Binaries/Intermediate 自动忽略）
├── docs/                           # [入库] 策划、规范、技术与运维文档
└── .github/                        # [入库] 自动化检查与协作模板
```

### 几个实用约定

1. **所有自制资产收口进 `Content/Dicebody/`**：不要把蓝图、贴图直接散落在 `Content/` 顶层。这样以后如果导入官方示例或插件素材，一眼就能分清哪些是我们自己做的，哪些是外部包。
2. **随手做实验去 `Content/Developers/<你的名字>/`**：想临时捏个材质、试个蓝图节点，先放自己的开发沙盒里；验证好用、改好标准名字（见 [UE5 命名规范](ue5-naming-conventions.md)）后，再迁进 `Content/Dicebody/` 正式目录并右键 **Fix Up Redirectors（修复重定向器）**。
3. **超大美术源工程别直接往仓库塞**：`.uasset`、导出好的 `.fbx` / `.png` / `.wav` 会自动走 Git LFS，但几十上百 MB 的 Substance Painter（`.spp`）、ZBrush、未压缩录屏视频很容易把 GitHub 免费 LFS 流量撑爆。这类超大源文件后续统一放团队共享网盘，仓库里只留引擎要用的导出成品（详见 [Git LFS 指南](../devops/git-lfs-guide.md)）。

---

## 4. 本地自动生成、绝不进仓库的文件夹

你打开过一次 UE5 工程或编译过一次 C++ 后，硬盘上会多出下面这些文件夹。`.gitignore` 已经把它们全拦住了，**千万不要手动强行 `git add -f` 提交它们**：

| 文件夹 / 文件 | 它是干嘛的 | 坏了能不能删？ |
| :--- | :--- | :--- |
| `Binaries/` | C++ 编译出来的 `.dll` / `.exe` | 可以删，重编代码或打开编辑器会重新生成 |
| `Intermediate/` | 编译中间文件、UnrealHeaderTool 生成代码 | 可以删，工程抽风打不开时常靠删它重编解决 |
| `Saved/` | 本地运行日志、报错崩溃记录、自动保存、截图 | 可以删（注意里面可能有你没手动 Ctrl+S 的自动备份） |
| `DerivedDataCache/` | 着色器与资产本地缓存（DDC） | 可以删，就是下次开编辑器要重新编译一遍着色器 |
| `Build/`、`StagedBuilds/` | 本地打包出来的测试包 | 可以删 |
| `.vs/`、`*.sln`、`.idea/` | Visual Studio / Rider 的本地工程与索引缓存 | 可以删，右键 `.uproject` → *Generate Visual Studio project files* 即可恢复 |

> **一句话省心记忆**：只要你没去碰 `Content/`、`Source/`、`Config/`、`Plugins/` 和 `docs/`，清理上面那些缓存文件夹不会丢掉任何正式成果。
