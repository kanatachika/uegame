# CI / CD 与自动化检查说明

这份文档用大白话说明：仓库里现在配了哪些 GitHub Actions“自动门卫”、PR 亮红灯了怎么排查，以及以后 UE5 工程真正落地后怎么接上自动编译和测试。

---

## 1. 现在仓库里有哪些自动检查？

所有流水线配置都在 `.github/workflows/` 目录下，目前有两份：

### 门卫 1：`repo-hygiene.yml`（仓库卫生检查 —— 已启用）

- **什么时候自动跑**：每次推送到 `main` 分支、每次提 Pull Request（PR），或者在 GitHub 网页的 `Actions` 页签里点 `Run workflow` 手动触发。
- **跑在哪儿**：GitHub 官方免费提供的 Linux 虚拟机（`ubuntu-latest`），几十秒跑完，不需要额外花钱。
- **不会烧 LFS 流量**：拉取代码时专门设置了 `lfs: false`，只检查 Git 记录里的指针和体积，不会下载大文件实体。
- **具体检查两件事**：
  1. **LFS 与大文件拦截**（脚本：`.github/scripts/check_lfs.py`）
     - 扫描所有已纳入 Git 管理的文件，检查有没有把 `.uasset`、`.umap`、`.fbx`、`.obj`、`.psd`、`.wav`、`.png`、`.tga`、`.exr`、`.mp4` 等 UE5 常见二进制资产直接塞进普通 Git（没走 LFS）。
     - 同时拦截任何**超过 10 MB** 且未走 LFS 的文件。
  2. **Markdown 规范与本地相对链接检查**（脚本：`.github/scripts/check_md_links.py`）
     - 扫描仓库里所有 `.md` 文件是否是合法 UTF-8 编码。
     - 检查所有指向仓库内其他文件的相对链接（完整支持中文文件名、URL 编码以及大小写校验），防止改名或移动文档后留下点不开的死链。

### 门卫 2：`ue5-ci-template.yml`（UE5 编译与测试模板 —— 预留待启用）

- **当前状态**：**只允许手动触发（`workflow_dispatch`），平时不会自动运行，绝对不会在当前的空工程阶段报错红灯。**
- **它以后负责什么**：
  1. **C++ 代码格式检查（`clang-format`）**：等 `Source/` 下有了 UE5 C++ 代码后，对照根目录 `.clang-format` 自动检查格式。哪怕现在手动点一下运行，它发现没有 `Source/` 也会自动跳过并亮绿灯。
  2. **UE5 工程编译与自动化测试**：预留好了调用 `Build.bat` 编译 Editor 目标、调用 `UnrealEditor-Cmd.exe` 跑 UE5 Automation Tests 并打包上传日志的完整骨架。默认开关 `run_ue5_build` 是关闭的，等接入自建构建机后再打开。

---

## 2. PR 亮红灯了怎么排查？

在 GitHub 的 PR 页面底部，如果看到红叉 `Some checks were not successful`，按这 3 步来：

1. **点红叉旁边的 `Details`**，打开失败的任务日志。
2. **找到标着 `[FAIL]` 的中文报错信息**，对号入座：
   - **如果是 `LFS 与大文件检查` 挂了**：
     - 日志会列出具体哪个文件没走 LFS 或超过了 10 MB，以及是“`.gitattributes` 漏配后缀”还是“你本机忘了跑 `git lfs install`”。
     - 直接照着日志末尾给的命令修，详细步骤看 [`git-lfs-guide.md`](./git-lfs-guide.md)。
   - **如果是 `Markdown 规范与相对链接检查` 挂了**：
     - 日志会直接标出 `文件名:行号 -> 找不到目标文件`。
     - 常见原因就 3 个：路径层级（`../`）多写或少写了一层、目标文件被改名/挪走了、或者**大小写没对齐**（Windows 不区分大小写，但 GitHub Actions 跑在 Linux 上严格区分 `README.md` 和 `readme.md`）。
3. **修完后直接提交并 push 到同一个分支**，PR 上的检查会自动重跑，变绿就可以合并了。

### 想在提交前先在自己电脑上自检？

只要电脑装了 Python 3，在仓库根目录直接跑这两条命令，结果和 GitHub Actions 里完全一样：

```powershell
python .github/scripts/check_lfs.py
python .github/scripts/check_md_links.py
```

---

## 3. 为什么 UE5 不能用 GitHub 免费云机器直接编译？

GitHub 免费版提供的云端虚拟机配置很有限（硬盘空间小、内存也不大，而且里面没有预装 Unreal Engine）。  
UE5 引擎本体装完动辄 40~60 GB，编一次项目又很吃 CPU 和内存，云端小机器既装不下也编不动。

所以 UE5 团队最常见、也最省钱的方案是：**用自己的 Windows 电脑注册成 GitHub Self-Hosted Runner（自建构建机）**——平时闲置的台式机或专门的打包机都可以。

---

## 4. 后续接入 UE5 自建构建机的路线图

我们按项目推进分三步走，绝不提前折腾用不上的基建：

### 阶段 1：当前阶段（文档定稿 + 仓库骨架）
- 只运行 `repo-hygiene.yml`（防大文件污染仓库 + 防文档死链）。
- 零硬件成本，零维护负担。

### 阶段 2：`.uproject` 与 `Source/` 落地后
- 依然不用急着上构建机，可以先打开 `ue5-ci-template.yml` 里注释掉的 `pull_request` 触发器，让免费的 Linux 机器自动帮大家检查 C++ 代码格式（`clang-format`）。

### 阶段 3：进入原型联调 / 多人写 C++ 与蓝图阶段
找一台装好同版本 UE5 和 Visual Studio 2022 的 Windows 机器，按下面步骤接进仓库：

1. **在 GitHub 上获取注册命令**：打开仓库的 `Settings` → `Actions` → `Runners` → `New self-hosted runner` → 选 `Windows`。
2. **给构建机打标签**：注册时在自定义标签里加上 `ue5`（让它的标签包含 `self-hosted, windows, ue5`，刚好和 `ue5-ci-template.yml` 里的 `runs-on` 对上）。
3. **配置引擎路径环境变量**：在构建机上设置系统环境变量 `UE5_ROOT`，指向本地 UE5 安装目录（例如 `C:\Program Files\Epic Games\UE_5.4`），然后重启 Runner 服务。
4. **先手动试跑一次**：在 GitHub `Actions` → `UE5 CI (Template)` → `Run workflow`，勾选 `run_ue5_build`，确认编译和自动化测试都能顺利跑通。
5. **再按需开启自动触发**：确认稳定后，把 `ue5-ci-template.yml` 里的 `if` 条件和触发器调整为只在 `main` 分支（或指定 PR）自动运行。

> **安全提醒（非常重要）**：  
> 如果本仓库保持为**公开仓库（Public）**，千万不要把自建构建机配置成“任何人提 PR 都自动触发”！否则陌生人提一个恶意 PR 就能在你的 Windows 电脑上执行任意命令。  
> 公开仓库下，自建构建机只应该对 **`main` 分支合并后** 或 **由团队成员手动 `workflow_dispatch`** 触发；只有把仓库设为私有（Private）且仅团队成员可见时，才建议对所有 PR 自动跑自建构建机。

---

## 相关文档

- [仓库总览（README）](../../README.md)
- [团队协作与提交流程（CONTRIBUTING）](../../CONTRIBUTING.md)
- [Git LFS 上手与避坑指南](./git-lfs-guide.md)
