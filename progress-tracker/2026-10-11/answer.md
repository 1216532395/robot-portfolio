# 回答：2026-10-11 的两个问题

> 问：[question.md](./question.md) ｜ 答：本文件
> 我**先查了你仓库的真实状态**再回答，所以下面的结论不是泛泛的建议，而是针对你 `F:\enbedded\repos\robot\` 的具体情况。

---

## 结论速览

| 你的问题 | 真正原因 | 一句话解法 |
|---|---|---|
| **Q1** GitHub 上只有 README.md，没有 .py | **不是上传失败** —— `d1_oscillator.py` 从来没被 `git add` + `git commit` 过。远端那个 commit 只含 README 和 .gitignore | 补一次 `git add` + `commit` + `push`；以后用 VS Code 源代码管理面板点两下 |
| **Q2** 新开 PowerShell 后跑不了代码 | **虚拟环境不会自动激活**。新窗口里 `python` 指向的是 Microsoft Store 版全局 Python（里面没装 numpy），于是 `ModuleNotFoundError` | **不用每次配置**。在 VS Code 里选一次解释器 `.venv\Scripts\python.exe`，以后终端自动带环境 |

顺带发现的 3 个小问题（不影响运行，但影响作品集），见 §5。

---

## Q1 · 为什么 GitHub 上只有 README.md

### 我查到的证据

`​.git/logs/HEAD` 里**只有一条真实提交**：

```
0000...000 → 19166663  commit (initial): chore: Day 1 repo skeleton
```

而 `.git/logs/refs/remotes/origin/main` 显示：

```
0000...000 → 19166663  update by push      ← 推送成功了，推的就是那一个 commit
```

**远端那个 commit 就是 Day1 §3.1「建骨架」时的提交，它不含代码。**
证据链：这条 commit 的信息是 `chore: Day 1 repo skeleton`，对应的正是 §3.1 的
`git add README.md .gitignore` —— 那时 `d1_oscillator.py` 还没写出来。而 §4.6 要求的那条
`feat(D1): ...` commit **在日志里完全不存在**。

而 §4.6 的「提交代码」那一步**没有被执行过**：

```powershell
git add d1_oscillator.py docs/d1_derivation.md   # ← 这一步没跑
git commit -m "feat(D1): ..."                     # ← 这一步也没跑
```

后面那 9 行 `Branch: renamed refs/heads/main to refs/heads/main`（重复的改名记录）说明你后来在 VS Code 里反复点过 Sync/Publish —— 那些操作都成功了，**只是仓库里本来就没有第二个 commit 可推**。

> ✅ 换句话说：你的网络、认证、remote、push 全都是通的。**问题只是"忘了 commit 代码"**，这是 Git 新手最常见也最无害的错误。

### 立刻修好（复制执行）

```powershell
cd F:\enbedded\repos\robot
.\.venv\Scripts\Activate.ps1          # 见 Q2，不激活也行，git 不需要 venv

git status                             # 应该看到 Untracked: d1_oscillator.py
git add d1_oscillator.py docs/d1_derivation.md
git commit -m "feat(D1): 三种数值积分解单自由度振子 + 自带 PASS/FAIL 自验证"
git push
```

### 你问的「有没有更简单的提交方式」—— 有，三选一

**方式 1：VS Code 图形界面（最推荐，从此不用记命令）**
```
左侧点「源代码管理」图标（分叉形状，或 Ctrl+Shift+G）
  →  Changes 列表里逐个文件点「+」（= git add）
  →  顶部输入框写一句提交信息
  →  点 Ctrl+Enter（= git commit）
  →  底部状态栏点「同步 / Sync Changes」（= push + pull 一步搞定）
```
在 `Changes` 面板上**每个文件都能看到它会不会被提交**，所以「忘了 add 代码」这种事以后不可能发生 —— 你这次的问题根源正是命令行下 `add` 被漏掉了。

**方式 2：一条命令完成 add + commit（配一次，永久用）**
```powershell
git config --global alias.ac '!git add -A && git commit -m'
# 以后提交只需：
git ac "feat(D1): 数值积分三方法对比"
git push
```
`-A` = 自动把所有新增/修改/删除的文件都纳入（受 .gitignore 约束），**再也不会漏文件**。

**方式 3：把「提交并推送」写成批处理，双击即可**
```powershell
# 文件：F:\enbedded\repos\robot\pushall.ps1
Set-Location $PSScriptRoot
git add -A
$msg = if ($args[0]) { $args[0] } else { "chore: update $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }
git commit -m $msg
git push
git show --stat HEAD        # 立刻自证这次到底提交了哪些文件
```
用法：`.\pushall.ps1 "docs: 填上 D1 推导"`

> 我的建议：**平时用方式 1（看得见），脚本化/批量时用方式 2。** 两种方式都保留最后一句 `git show --stat`，因为它才是"我真的提交了吗"的答案。

### 验证过程（必须做这两步确认成功）

**① 本地验证**（确认文件真的进了版本库，而不是你以为进去了）：
```powershell
git show --stat HEAD
```
期望看到：
```
commit xxxxx
    feat(D1): 三种数值积分解单自由度振子 + 自带 PASS/FAIL 自验证
 d1_oscillator.py    | 112 +++++++++++++++++++
 docs/d1_derivation.md |  ...
```
> ⭐ **`git show --stat HEAD` 是判断"提交里到底有什么"的唯一可靠方法。**
> `git status` 只显示「工作区和暂存区的差异」，它**不显示已提交的内容**——很多人误以为「status 干净 = 都传上去了」，其实干净只意味着「本地 = 本地仓库」，跟 GitHub 无关。

**② 远端验证**：浏览器打开
`https://github.com/1216532395/robot-portfolio` → 应该看到 `d1_oscillator.py`。
或命令行：
```powershell
git ls-files --others --exclude-standard      # 期望：空（没有漏掉的未跟踪文件）
git log origin/main --oneline                  # 期望：能看到你刚推的那条
```

### 为什么 .gitignore 里的 `*.png` 会让图也传不上

你现在仓库里没有 `d1_result.png` 的记录，是因为 `.gitignore` 第 3 行 `*.png` 把它挡住了（这是 Day1 文档故意设计的——大图别进 Git）。

但如果你想**把实验图放进作品集 README 里展示**（很值得！有图有曲线的 README 在面试里加分明显），就把 `.gitignore` 里那行 `*.png` 删掉。

**推荐直接把整个 `.gitignore` 换成下面这份**（只排除虚拟环境和缓存）：
```gitignore
.venv/
__pycache__/
.pytest_cache/
*.pyc
```
这样代码、笔记、`d1_result.png`、`Figure_1.png` 都能进仓库。
> 原则：**虚拟环境（几千个文件、几百 MB）绝不进 Git；你自己写的代码、笔记、实验图都要进 Git。**
> 改完记得 `git add .gitignore d1_result.png`，再用 `git status` 确认图已经出现在待提交列表里。

---

## Q2 · 每次开 PowerShell 到底要不要重新配置环境

### 真正发生了什么

你的虚拟环境里 **numpy/scipy/matplotlib 都装好了**（我查了 `.venv\Lib\site-packages\`：numpy、scipy、matplotlib、PIL、fontTools 都在，Python 是 3.11.9）。

但**虚拟环境的作用范围是"当前这个窗口"**：

| 你做的事 | 结果 |
|---|---|
| 窗口 A：`Activate.ps1` → `python d1_oscillator.py` | ✅ 能跑（`python` 指向 `.venv\Scripts\python.exe`） |
| 关掉窗口，开窗口 B：直接 `python d1_oscillator.py` | ❌ `ModuleNotFoundError: No module named 'numpy'` |

因为窗口 B 里 `python` 又变回**全局 Python**（从 `.venv\pyvenv.cfg` 看，你装的是 **Microsoft Store 版** `WindowsApps\PythonSoftwareFoundation.Python.3.11`），那个里面没装 numpy。

> 📌 **你不需要"每次配置环境"。环境已经配好了，只是每个新窗口要"打开门"（激活）一次。**
> 而且**有一个办法让你连"开门"都不用**——见方案 1。

### 方案 1（强烈推荐）：全部在 VS Code 里做，激活这一步自动消失

你问「能不能直接在 VS Code 里完成」—— **能，而且这就是正确做法。** VS Code 选定解释器后，它每次给你开新终端都会**自动帮你激活虚拟环境**。

一次性配置（只做一次，永久生效）：
```
1. VS Code → 文件 → 打开文件夹 → F:\enbedded\repos\robot
2. Ctrl+Shift+P → 输入「Python: Select Interpreter」→ 选
   .venv\Scripts\python.exe        （列表里通常标着 "Recommended" 或 ('.venv')）
3. 装扩展：Python（Microsoft）、中文语言包（可选）
4. 以后直接点右上角 ▶ 运行按钮，或 Ctrl+Shift+` 开终端敲 python
```

**验证（这一步是关键，做给你自己看）**：
```
Ctrl+Shift+`  新开一个终端（全新窗口！）
PS F:\enbedded\repos\robot> python -c "import numpy; print(numpy.__version__)"
```
✅ 通过标准，两条都要满足：
1. 打印出版本号（如 `2.1.3`），**没有报错**；
2. 命令行提示符**前面出现 `(.venv)`** —— 这就证明 VS Code 自动激活了。

再看一眼用的到底是哪个 python：
```powershell
python -c "import sys; print(sys.executable)"
# 期望：F:\enbedded\repos\robot\.venv\Scripts\python.exe
# 若显示 ...\WindowsApps\... ⇒ 没激活成功，回到第 2 步重选解释器
```
> ⭐ **`sys.executable` 是排查"我到底在用哪个 Python"的万能钥匙。** 记住这一行，以后所有「装了但 import 不到」的问题都靠它 30 秒定位。

然后在 VS Code 里点 `d1_oscillator.py` 右上角 ▶，终端直接出结果 —— **全程不用手敲 activate。**

### 方案 2：坚持用独立 PowerShell 窗口时的两个办法

**A. 每次开头敲一行（最透明，推荐新手先用这个养成习惯）**
```powershell
cd F:\enbedded\repos\robot
.\.venv\Scripts\Activate.ps1
python d1_oscillator.py
```

**B. 用绝对路径调用，根本不激活**（偶尔跑一个脚本时很方便）
```powershell
F:\enbedded\repos\robot\.venv\Scripts\python.exe d1_oscillator.py
```

**C. 不想每次 cd（把项目加成一个"命令")**
做一个 `run.ps1` 放仓库根，双击/一条命令搞定：
```powershell
# 文件：F:\enbedded\repos\robot\run.ps1
Set-Location $PSScriptRoot
. .\.venv\Scripts\Activate.ps1
python @args          # 把后面所有参数原样传给 python
```
用法：`.\run.ps1 d1_oscillator.py`

### 关于「关掉再开就报执行策略错误」

如果新窗口 `Activate.ps1` 报 `无法加载文件 ... 因为在此系统上禁止运行脚本`：
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
只需做一次（只对当前用户放宽，安全）。或者干脆用不依赖策略的写法：
```powershell
.\.venv\Scripts\activate.bat        # cmd 版；在 PowerShell 里也可用下面这条
cmd /c ".\.venv\Scripts\activate.bat && python d1_oscillator.py"
```
> 但如果你走**方案 1（VS Code）**，这个坑基本不会再遇到。

### 要不要考虑换掉 Microsoft Store 版 Python？

**现在不用换，能跑就行。** 但要知道它有这些已知别扭之处（以后碰到怪问题再回来换）：
- 路径在 `WindowsApps\` 下，带一串随机字符，别的工具找不到；
- 偶尔因为权限/同步机制导致 pip 装完 import 不到；
- 装 CUDA / 某些科学计算库时不如官方版方便（**大三阶段 M-D 要训练模型时会遇到**）。

真要不要换的话（Day 2 之前换成本最低）：
```powershell
winget install -e --id Python.Python.3.12
cd F:\enbedded\repos\robot
Remove-Item -Recurse -Force .venv      # 删掉旧虚拟环境（10 秒可重建，别心疼）
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip numpy scipy matplotlib
```
> 换的是**虚拟环境**，不是重装一遍库到系统里。虚拟环境是消耗品，删了重建只要 1 分钟——这个认知能让你以后敢随便折腾。

---

## 5 · 顺带发现的三个小问题（现在改掉，5 分钟）

### ① `dt` 还停在破坏性实验的值上 ⚠️ 影响你今天的结论

[d1_oscillator.py](../../d1_oscillator.py) 第 63 行现在是：
```python
dt = 0.05          # ← Day1 §4.5 破坏性实验留下的值，没改回来
```
Day1 文档 §4.5 要求实验做完**改回 `0.01`**。现在跑会看到 `[4]` 报 `[FAIL]` —— 那是**预期现象**（Δt 太大 → RK4 相位误差累积），但你如果忘了这茬，会误以为脚本有 bug。

```python
dt = 0.01          # 改回来，5 行断言应全部 [PASS]
```
**验证**：`python d1_oscillator.py`，期望 `[1]..[5]` 五个 `[PASS]`，且 `[1]` 的振幅 ≈ 7.1。

### ② 两个文件是空的，但 Day1 文档要求写内容 ⚠️ 这是作品集的缺口

我读了这两个文件，都是 **0 字节**：
- [2026-10-11.md](./2026-10-11.md)（今天的周记录）
- [../docs/d1_derivation.md](../../docs/d1_derivation.md)（今天的推导）

它们现在还是「文件名存在，内容为空」。按 [机器人控制教程](../../../机器人控制教程-从0到就业.md) §3 的原则——**「推导一遍 + 代码画一遍」三者缺一不算掌握**，推导那一半还欠着。把 Day1 §4.1 那四行抄进去，再加上你自己的失败样本，才算完成：

```markdown
# D1 · 单自由度无阻尼振子的三种数值解
模型：ẍ + 2ζωn ẋ + ωn² x = 0，状态 s=[x,v]，ωn=2π，x0=1, v0=0
无阻尼解析解：x(t)=cos(ωn t) → 振幅恒为 1
显式欧拉每步放大因子 |λ| = sqrt(1+ωn²Δt²) > 1 → 与 Δt 多小无关，必发散
Δt=0.01 预测：(1.00395)^500 ≈ 7.1
实测：欧拉 ____，辛欧拉 ____，RK4 误差 ____，收敛阶比 ____
结论：仿真发散先查积分器与步长，再查单位符号，最后才怀疑控制器
```

### ③ 仓库里有个 `新建 文本文档.txt`（空文件）

```powershell
Remove-Item "F:\enbedded\repos\robot\新建 文本文档.txt"
```
不影响任何东西，但作品集仓库里留着它会让 README 的第一印象差一点。顺手清掉。

---

## 6 · 完成后请把这张表打勾（写回 question.md 下面也行）

```
[ ] git show --stat HEAD  能看到 d1_oscillator.py（本地已提交）
[ ] GitHub 网页上能看到 d1_oscillator.py（远端已推送）
[ ] VS Code 已选定解释器 .venv\Scripts\python.exe
[ ] 新开一个 VS Code 终端：提示符带 (.venv)，且 import numpy 成功
[ ] python -c "import sys; print(sys.executable)" 指向 .venv
[ ] dt 改回 0.01，跑出的 5 行全部 [PASS]，且记下三个数字
[ ] docs/d1_derivation.md 填上推导 + 实测数字（不再是 0 字节）
[ ] progress-tracker/2026-10-11/2026-10-11.md 填上今日记录与明日第一步
```

全勾 → 今天正式通关 [Day1](../../../Day1-环境搭建与首次验证.md)，明天做 **Day 2：WSL2 + Ubuntu**（放周末长块）。

---

## 7 · 一句话记住的两条原理

1. **Git 有三个地方**：工作区（你的文件）→ 暂存区（`git add`）→ 本地仓库（`git commit`）→ 远端（`git push`）。
   **GitHub 上少文件，99% 是中间某一环没走**，而不是「上传方式不好」。
   查真相用 `git show --stat HEAD`，别看 `git status`。
2. **虚拟环境 = 一个文件夹里的假 python**，激活只是「把 PATH 临时改到这个文件夹」。
   关窗口 = PATH 复原 = 又用回系统 python。**所以不是环境坏了，是门没开。**
   查真相用 `python -c "import sys; print(sys.executable)"`。

---

*回答文件：`F:\enbedded\repos\robot\progress-tracker\2026-10-11\answer.md`*
