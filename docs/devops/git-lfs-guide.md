# Git LFS 上手指南（给队友的大白话手册）

## 1. 先搞懂：为啥 UE5 项目一定要用 Git LFS？

普通的 Git 是给纯文本代码设计的（每次改动只存几行文字差异）。  
但 UE5 的蓝图（`.uasset`）、关卡（`.umap`）、模型（`.fbx`）、贴图（`.png` / `.tga` / `.exr`）、音频（`.wav`）全是**二进制大文件**，哪怕只微调了一个数值，普通 Git 也会把整个几十 MB 的文件再存一份。

时间一长，仓库体积会飙到几十 GB，拉代码慢到怀疑人生，GitHub 也会直接拒收超过 100 MB 的单文件。

**Git LFS（Large File Storage）干的事很简单**：  
把大文件单独存到 GitHub 的大文件空间里，Git 仓库本体只留一张 130 字节左右的“提货单”。你拉代码时它自动帮你把真实文件换回来，平时几乎无感。

---

## 2. 首次准备：Windows 安装与启用（每台电脑只做一次）

### 第 1 步：确认电脑上有没有装 Git LFS

打开 PowerShell 或终端，输入：

```powershell
git lfs version
```

- 如果输出类似 `git-lfs/3.x.x ...`，说明已经装好了（新版 Git for Windows 一般自带），直接跳到第 2 步。
- 如果提示找不到命令，用下面任意一种方式安装：
  - **方式 A（推荐，命令行一键装）**：
    ```powershell
    winget install -e --id GitHub.GitLFS
    ```
  - **方式 B（官网安装包）**：到 [git-lfs.com](https://git-lfs.com/) 下载 Windows 安装包，一路下一步即可。

### 第 2 步：全局启用 Git LFS（最容易忘的一步！）

装完之后，**必须**在终端里跑一次：

```powershell
git lfs install
```

看到 `Git LFS initialized.` 才算真正打开开关。

> **千万别漏这步**：如果你没跑 `git lfs install` 就直接 `git add` 并提交 `.uasset`，即使仓库的 [`.gitattributes`](../../.gitattributes) 已经配好了规则，你电脑上的 Git 也会跳过 LFS，把大文件硬塞进普通 Git 里——然后提 PR 时会被 CI 门卫拦截。

---

## 3. 首次拉取仓库（Clone）

装好并执行过 `git lfs install` 后，正常拉仓库就行：

```powershell
git clone https://github.com/kanatachika/uegame.git
cd uegame
```

**如果你不小心先 `git clone` 了，后来才装的 Git LFS**：  
不用删掉重新拉，进到仓库目录补两条命令就行：

```powershell
git lfs install
git lfs pull
```

---

## 4. 怎么确认自己的文件真的走了 LFS？

提交前花 3 秒看一眼，比提 PR 亮红灯后再返工省事得多：

1. **看当前准备提交的文件**：
   ```powershell
   git lfs status
   ```
   如果看到文件名后面标着 `(LFS: ...)`，说明没问题；如果标着 `(Git: ...)` 但它是个 `.uasset` / `.fbx` / `.wav`，说明漏配了或没装 LFS。

2. **看仓库里哪些文件已经在 LFS 里**：
   ```powershell
   git lfs ls-files
   ```

3. **查某个路径会命中什么规则**（不用文件真实存在也能测）：
   ```powershell
   git check-attr -a Content/Maps/TestMap.umap
   ```
   正常应该能看到 `filter: lfs` 和 `lockable: set`。

哪些后缀默认走 LFS，统一写在根目录的 [`.gitattributes`](../../.gitattributes) 里。如果你以后引入了新格式的二进制大文件（比如 `.blend`、`.psd` 等且 `.gitattributes` 里还没写），先加一条规则再提交：

```powershell
git lfs track "*.blend"
git add .gitattributes
```

---

## 5. 多人协作必看：文件锁（`git lfs lock` / `unlock`）

### 为什么要锁文件？

代码（`.cpp` / `.h` / `.md`）两个人同时改同一个文件，Git 往往能自动合并；  
但 UE5 的 **`.uasset`（蓝图/材质/数据表）和 `.umap`（关卡）是二进制文件，Git 绝对合不了**。如果两个人同时改了同一张图，后提交的人要么覆盖掉队友的活，要么只能把自己的重做一遍。

所以我们在 [`.gitattributes`](../../.gitattributes) 里给 `.uasset` 和 `.umap` 开了 `lockable`（可加锁）。

### 日常三步操作

1. **动工前先抢锁**：
   ```powershell
   git lfs lock Content/Maps/Greybox_01.umap
   ```
   如果已经有人锁了，终端会直接告诉你目前是谁占着这文件，群里打声招呼就行。

2. **随时看现在谁锁了哪些文件**：
   ```powershell
   git lfs locks
   ```

3. **改完提交、推上去后，记得解锁！**
   ```powershell
   git lfs unlock Content/Maps/Greybox_01.umap
   ```

> **常见小坑提醒**：  
> 配了 `lockable` 的文件，在你没锁它的时候，Git 会故意把它设成**只读（Read-Only）**防止你误改。  
> 如果你在 UE5 编辑器里点保存时弹出“文件只读无法保存”，**不要手动去 Windows 属性里取消只读**——先切回终端 `git lfs lock <文件路径>`，它会自动变成可写，保护你和队友不互相覆盖。

### 队友锁完人找不到了怎么办？

确认对方已经不需要改动（最好先在群里说一声），可以用强行解锁：

```powershell
git lfs unlock --force Content/Maps/Greybox_01.umap
```

---

## 6. 不小心把大文件直接塞进普通 Git 了怎么补救？

### 情况 A：还没 `git commit`（只在暂存区）

```powershell
git lfs install
git rm --cached <那个文件路径>
git add <那个文件路径>
git lfs status
```

看到变成 `(LFS: ...)` 再提交即可。

### 情况 B：已经 `git commit` 了，但还没 `git push`

如果只是本地还没推上去的提交漏走了 LFS，用 `migrate` 自动把未推送的提交转成 LFS（最干净，不会把大文件残留进历史）：

```powershell
git lfs install
# 如果是新后缀，先补规则：git lfs track "*.xxx" 并提交 .gitattributes
git lfs migrate import --include="*.uasset"
```

如果已经推到远端分支、不想改写提交历史，只想补一次新提交把当前文件转成 LFS：

```powershell
git lfs migrate import --no-rewrite <文件路径>
```

如果不确定历史里混进了几个，或者已经被 PR 里的 CI 拦下来，可以把报错日志发群里一起处理，避免误操作改坏提交记录。

---

## 7. GitHub 免费版 LFS 额度避坑提醒（必读！）

目前仓库托管在 GitHub 免费版，免费账号的 Git LFS 额度很抠门：

- **存储空间**：免费 **1 GB**
- **月度下载流量**：免费 **1 GB / 月**（注意：每个队友 `git clone` 或 `git lfs pull` 下载文件都会算流量！）

一旦超额，GitHub 会暂时禁止整个仓库拉取 LFS 文件，直到下个月重置或者购买流量包（官方约 $5 / 月，买 1 份给 50 GB 存储 + 50 GB 流量）。

### 省流量、不踩雷的 4 个习惯

1. **别把巨型临时素材丢进仓库**：比如几百 MB 的录屏原片、未压缩的 4K 贴图源文件、网上下的完整免费素材包（只挑项目里真用得到的放进 `Content/`）。
2. **别动不动删掉整个项目目录重新 `git clone`**：每次重新 clone 都会把仓库里所有 LFS 文件再下一遍，几个人各删一次，1 GB 流量当天就没了。平时更新代码用 `git pull` 就行。
3. **CI 已做了省流量处理**：我们的自动检查流水线（见 [`ci-cd-overview.md`](./ci-cd-overview.md)）拉代码时专门关掉了 LFS 下载（`lfs: false`），不会白白帮我们烧流量。
4. **提前有心理准备**：灰盒原型阶段资产很小，免费额度够用；等以后进美术量产、资产超过 1 GB 时，再按需买 1 份 GitHub LFS Data Pack，或者切到对象存储 / 自建 Git 服务器。

---

## 相关文档

- [团队协作与提交流程（CONTRIBUTING）](../../CONTRIBUTING.md)
- [CI / CD 自动化检查与构建机说明](./ci-cd-overview.md)
- [仓库根目录 `.gitattributes` 规则文件](../../.gitattributes)
