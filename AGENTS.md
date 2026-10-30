# AGENTS.md — 传鹏实验室网站维护指南

**生成时间**: 2026-08-01
**技术栈**: Hugo 0.102.3 + blogdown (R) + Wowchemy Academic v5 + Netlify
**性质**: 双语实验室网站（英文 `content/en/` + 中文 `content/zh/`）。所有内容必须 en/zh 双份同步，否则 CI 变红。

本指南供**实验室成员**更新网站内容时使用（自己操作，或指挥 AI 代理操作），范围只有三件事：**更新成员信息**、**更新论文信息**、**更新博客**。规划中的功能（News 栏、X feed 等）**不在本指南范围**，见 [FuturePlan.md](FuturePlan.md)。

---

## 项目结构

```
content/
  en/  zh/                        # 中英文内容（结构完全一致，必须同步维护）
    project/{姓名全拼}/index.md   # 团队成员（+ featured.jpg 头像）
    publication/{年份_类型_作者}/  # 论文（index.md + cite.bib）
    post/{日期-标题}/index.md     # 博客文章
    authors/admin/_index.md       # PI 介绍
    home/                         # 首页模块
config/_default/                  # 站点配置（menus.yaml / menus.zh.yaml 导航菜单）
templates/                        # 内容模板（成员/论文/博客，填写后由脚本自动更新）
.github/scripts/                  # CI 辅助脚本（校验 + 生成 + 离组自动化）
.github/workflows/check-content.yml  # CI：front matter 校验 + 中英同步 + 校友一致性
to_be_added_pubs/                 # 待添加论文的 BibTeX 暂存区（gitignored）
```

---

## 模板化工作流（推荐）

**提交区模式**：`templates/` 下有三个提交区子文件夹。填写信息放入对应子文件夹 → 运行脚本 → 自动对比去重、未添加则生成 en/zh 文件（含图片）、处理完归档到 `_done/`。

| 任务 | 提交区 | 脚本 | 自动完成 |
|---|---|---|---|
| 新成员加入 | `templates/member/` | `add_member.py` | 建 en/zh 文件夹 + index.md + 头像 featured.jpg；按姓名/文件夹去重 |
| 添加论文 | `templates/publication/` | `add_publication.py` | 建 en/zh 文件夹 + index.md + cite.bib；Crossref 补卷期/摘要；按 DOI/标题去重 |
| 添加博客 | `templates/post/` | `add_post.py` | 建 en/zh post 文件夹；单语言自动加豁免名单；按 date-title 去重 |

子文件夹内的 `_template.md` 是示例模板（`_` 前缀文件会被脚本跳过）；也可直接用 `templates/new_*.md` 顶层模板填写。

示例：
```bash
# 1. 把填写好的 姓名.md + featured.jpg 放入 templates/member/
# 2. 运行脚本（自动扫描整个提交区）
/tmp/opencode/ci-venv/bin/python .github/scripts/add_member.py templates/member/
/tmp/opencode/ci-venv/bin/python .github/scripts/add_publication.py templates/publication/
/tmp/opencode/ci-venv/bin/python .github/scripts/add_post.py templates/post/
```
脚本支持 `--dry-run` 预览；处理成功的文件自动移到提交区 `_done/` 子目录；生成后跑校验脚本确认全绿。

## 任务一：更新成员信息

### 新成员加入（成员可自行填写，管理员审核）
1. **文件夹命名**：姓名全拼（姓+名拼接、各音节首字母大写），如 `HuangYijie`、`HuChuanpeng`。en/zh 各建一份。
2. **`index.md` 关键字段**：
   - `title`/`image.caption`：中文名（zh）/ 英文名（en）
   - `tags`：角色标签，只能是其一 →
     `Principal Investigator` | `Research Assistants` | `Postgraduate` | `Undergraduate` | `Alumni`
   - `summary`：`__Sep. 2024 ~ Now__ <br/> 一句话简介`（时间范围用英文格式）
   - `links`：github/twitter 等（可选）
3. **头像**：`featured.jpg`（建议 <500KB）
4. 正文（front matter 下方）写个人简介，支持 Markdown/HTML
5. **中英文都要建**（CI 同步检查强制）

### 成员离组（推荐用脚本）
```bash
python .github/scripts/mark_alumni.py <姓名全拼> --end "2026"
```
- 自动完成：`tags` → `Alumni` + `summary` 时间范围 `__Sep. 2024 ~ Now__` → `__Sep. 2024 ~ 2026__`（en/zh 同时）
- `--start` 可省略（自动读取现有起始时间）；加 `--dry-run` 可预览不写入
- 脚本不处理：正文中"在读"等时效信息 → 需人工检查更新

---

## 任务二：更新论文信息

### 添加新论文
1. **文件夹命名**：`{年份}_Publication_{第一作者}`（正式发表）或 `{年份}_Preprint_{第一作者}`（预印本）。en/zh 各一份。
   - 同作者多篇消歧：加后缀（如 `Ren_ZL`/`Ren_ZW`、`Yue_RR`/`Yue_grassroots`）
2. **`index.md` 关键字段**：
   - `abstract`：**含冒号 `:` 的值必须用双引号包裹**（最常见构建失败原因）
   - `authors`：每行一位
   - `doi`、`date`/`publishDate`（`YYYY-MM-DDT00:00:00Z`）
   - `publication`/`publication_short`：期刊名
   - `publication_types`：**主题固定编号** `"1"`=会议 `"2"`=期刊 `"3"`=预印本 `"4"`=报告 `"5"`=书 `"6"`=书章节 `"7"`=学位论文 `"8"`=专利
   - `projects`：关联成员文件夹名（可选）
   - `url_source`：预印本填平台链接（PsyArXiv/ChinaXiv/bioRxiv 等）
3. **`cite.bib`**：BibTeX 条目（字段带逗号、条目类型正确 @article/@misc，勿用 @inproceedings 标期刊论文）
4. **数据来源**：`to_be_added_pubs/Exported Items.bib` 可直接提取
5. **卷期号**：可用 DOI 查 Crossref API（`https://api.crossref.org/works/{doi}`）回填 `volume`/`number`

### 中文论文的英文页（`content/en/`）

中文论文在 en 侧必须英文化（zh 侧保持中文），**不能把中文原样留在 en**：

- `title`：官方英文标题 + ` (in Chinese)`，例：`Measurement reliability of cognitive tasks: current trends and future directions (in Chinese)`
- `abstract` / `summary`：用官方英文摘要；**无官方英文版则不翻译，留空 `""`**
- `authors`：英文姓名（`Given Family` 或 `Family, Given` 择一），勿写成 `Chuan-Peng, H` 这类姓名反转式
- `publication` / `publication_short`：英文刊名，如 `In *Chinese Science Bulletin*`
- `cite.bib` 同步英文化：`title`（含 `(in Chinese)`）、`author`（用 `and` 分隔，勿用逗号）、`journal`、`keywords`；en `abstract` 留空时删掉 bib 里的中文 `abstract`
- `index.md` **没有 `keywords` 字段**，关键词只写在 `cite.bib`
- 英文标题来源：期刊英文页 / ChinaXiv（`chinaxiv.org/abs/{id}`，中英标题并列）/ Crossref；CNKI 有验证码不可抓

自查（应无输出）：

```bash
python3 -c "import glob,re;[print(f) for f in glob.glob('content/en/publication/*/*') if f.endswith(('.md','.bib')) and re.search(r'[\u4e00-\u9fff]',open(f,encoding='utf-8').read())]"
```

### 成员-论文自动关联（`add_publication.py` 内置）

用 `add_publication.py` 添加论文时，脚本会自动比对作者与成员：

- **全名匹配**（如 `Siyu Chen`、`任子伟`、`Zheng Liu`；兼容"姓前名后/名前姓后"与中英别名如 `YuKi (Mengzhen Hu)`）→ 自动写入 `projects:`（en/zh 同步）
- **缩写作者**（如 `Liu, Y`、`Duan S`、`Hu, C-P`，无法可靠确认身份）→ 仅在控制台提示候选成员，**不自动关联**，需人工确认后补写 `projects:`
- **PI 胡传鹏**不参与自动关联（他的个人页不列论文）
- 人工确认缩写对应关系后，可直接编辑论文 `index.md` 的 `projects:` 字段补充（en/zh 都要改）

### 预印本转正式发表
1. 新建正式版文件夹（`{年份}_Publication_{作者}`）
2. 更新元数据：`doi`、`publication`、`publication_types`（"3"→"2"）等
3. 删除原预印本文件夹（en/zh 都操作）

---

## 任务三：更新博客

1. **文件夹**：`content/{en,zh}/post/{日期-标题}/index.md`
2. **front matter**：`title`、`date`、`summary`、`tags`
3. **默认中英都要建**；旧文章也可直接放 `content/{en,zh}/post/` 下（如 `2019-04-29-xxx.md`）
4. **只需一种语言时**：必须把差异加入 `.github/scripts/i18n_allowlist.txt`（格式 `[ZH only] post/2026-01-01-xxx`，一行一条），否则 CI 中英同步检查标红；补齐双语后移出该行

---

## 全局规则（所有任务强制）

- **会话第一步：检查本地仓库是否为最新**：每次会话开始，先运行 `git fetch` 并确认本地在 `main` 分支与 `origin/main` 同步（`git status` 无落后、无未提交改动）；若本地落后，先 `git pull`（或 `git rebase`）再开始任何修改，避免基于过期内容工作
- **en/zh 同步**：改任何内容，两种语言都要改（CI 校验）
- **YAML front matter**：值含冒号/特殊字符 → 双引号包裹
- **文件夹重命名**：用 `git mv` 保留历史；改文件夹名后检查 `projects:` 引用
- **提交规范**：PLAIN English 风格，如 "add new member xxx"、"mark xxx as Alumni"
- **验证**：改完跑 CI 脚本（见下）确认全绿再提交；**最终以 CI 结果为准**，本地绿 ≠ CI 绿（见下文 N5）

## 多人多机协作约定（本地不报错，只在 CI 或他人机器上暴露）

成员在各自电脑上操作（macOS / Windows、不同 Python 与 Hugo 版本、仓库可能位于 OneDrive 等同步目录）。以下五类问题**在本机表现完全正常**，提交前必须自查，否则只会在 CI 或他人机器上炸。

### N1 文件名大小写

- **规则**：文件夹名与规范**逐字符一致**（`HuChuanpeng`，不是 `huchuanpeng` / `HUCHUANPENG`）。macOS 默认大小写不敏感，写错了本地照样能打开；而 CI 只在 en/zh 两侧写得不一致时才会红（见 N5），两边一起写错则完全无感知，问题会留到线上。
- 文件夹名不要含**空格**（历史遗留的 `2023_Publication_Chen zhiyi1` / `2` 保持现状，不要照抄）。
- **自查**（列出所有成员文件夹名，逐个核对大小写）：
  ```bash
  git ls-files content/en/project content/zh/project | cut -d/ -f4 | sort -u
  ```
- **修正**：macOS 上直接 `git mv Foo foo` 不会生效（文件系统认为同名），必须分两步：
  ```bash
  git mv Huchuanpeng tmp_case && git mv tmp_case HuChuanpeng
  ```

### N2 编码与换行符

- **规则**：`.md` / `.bib` 必须 **UTF-8 无 BOM**；**进入 git 的换行必须是 LF**。
- 换行由 git 统一管，不靠各人手工统一：仓库 `.gitattributes` 已设 `* text=auto`，提交时自动归一化为 LF。工作区看到 CRLF 还是 LF，取决于**本机** `core.autocrlf`（当前这台是 `true`，所以本地文件是 CRLF）——这是正常的，**不要手工批量转 LF**，否则会给全库制造无意义的 diff。
- 真正的跨机器风险是 **BOM**：Windows 编辑器常默认加 BOM。带 BOM 时 `validate_frontmatter.py` 认不出首行的 `---`，会把整个文件**静默跳过**（不报错），Hugo 侧同样丢失元数据——属于无声失败，只能靠下面的自查发现。VS Code 右下角编码选 `UTF-8`（**不是** `UTF-8 with BOM`）。
- **自查**（两条都应无输出）：
  ```bash
  git ls-files --eol content | grep -E '^i/(crlf|mixed)'   # 提交层仍是 CRLF 的文件
  git grep -lI $'\xef\xbb\xbf' -- content                  # 带 BOM 的文件
  ```
- **已知例外**：`content/en/authors/admin/_index.md` 历史上以 CRLF 提交（`i/crlf`），下次改动该文件时会自动归一化，无需单独提交换行修正。

### N3 提交区是共享目录（会被他人的文件牵连）

- `templates/member|publication|post/` **入库且多人共用**，脚本会扫描其中**全部**文件——别人的半成品会和你的一起被处理、一起发布。
- 规则：
  1. 放入前先跑 `git status templates/`；若存在他人未处理的文件，**不要替别人发布**，先确认或等对方处理完。
  2. 自己的文件加姓名前缀（如 `HuChuanpeng-new-member.md`），便于归属识别。
  3. **先 `--dry-run`**，确认输出只涉及自己的文件，再正式执行。
  4. 不放测试/占位文件；草稿用 `_` 前缀（脚本会跳过）。

### N4 `_done/` 归档冲突

- 脚本把处理完的源文件移入本提交区的 `_done/`。该目录 **gitignored**，不会进 git，也不会有跨机器覆盖或冲突；风险仅限**本机**重复归档时的同名覆盖。
- 规则：跑完用 `ls` 看一眼 `_done/`（它被忽略，`git status` 里看不到）；发现同名文件时先确认是不是自己又要重新处理的，必要时改名为 `{原文件名}-{姓名全拼}`，不要静默覆盖。

### N5 本地绿 ≠ CI 绿

- 本地脚本只代表**你这台机器**（Python 版本、文件系统、locale）通过；`.github/workflows/check-content.yml` 才是最终裁决。
- CI 只跑三个脚本（front matter / i18n / alumni），**不构建站点**，也**不检查大小写与 BOM**——这两项 CI 兜不住，只能靠 N1 / N2 自查。
- 分工：CI 管"front matter 合法、en/zh 目录对称、Alumni 元数据"；本地自查管"大小写、BOM、站点能否正常构建"。
- 合并前必须确认 CI 全绿。若 CI 红在 i18n 这一项，**优先排查 N1**（同一文件夹在 en/zh 两侧写法不一致），再查是否真的漏建了对应语言。

## 常用命令

```bash
Rscript -e "blogdown::serve_site()"                     # 本地预览
Rscript -e "blogdown::build_site()"                     # 构建（注意 'public' 坑）
python3 .github/scripts/check_i18n_sync.py              # 中英同步检查
python3 .github/scripts/check_alumni.py                 # 校友一致性
python3 .github/scripts/mark_alumni.py <名字> --end "2026"  # 成员离组
python3 .github/scripts/validate_frontmatter.py           # front matter 校验（需 PyYAML+tomllib，见"已知坑"）
```

## 已知坑

- **`'public'` 垃圾目录**：经 Rscript（非 RStudio）跑 `blogdown::build_site()` 会在根目录生成名字含引号的 `'public'` 目录（blogdown 转义 `-d 'public'` 参数，system2 不经 shell 传引号给 hugo）。删除：`rm -rf "'public'"`
- **`public/` 是构建产物**（gitignored），不要提交
- **`.sisyphus/`** 是工作文件（gitignored）
- **系统 python3 缺依赖**：`validate_frontmatter.py` 需 `PyYAML` + `tomllib`（Python ≥3.11）。`/usr/bin/python3` 有 yaml 无 tomllib，Homebrew python 反之 → 缺 tomllib 时用 `/usr/bin/python3` 跑仅 YAML 的等价检查即可（本仓库 TOML front matter 只有 `home/demo*.md` 4 个文件）
- **Crossref 查询**注意限速（间隔 ≥0.5s）和 404（中文期刊/预印本多无记录）
