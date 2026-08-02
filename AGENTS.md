# AGENTS.md — 传鹏实验室网站维护指南

**生成时间**: 2026-08-01
**技术栈**: Hugo 0.102.3 + blogdown (R) + Wowchemy Academic v5 + Netlify
**性质**: 双语实验室网站（英文 `content/en/` + 中文 `content/zh/`）。所有内容必须 en/zh 双份同步，否则 CI 变红。

本指南面向 AI 代理，核心职责有三：**更新成员信息**、**更新论文信息**、**更新博客**。

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

## 任务四：待办任务（To-Do，尚未实现）

以下为规划中的功能增强，**2026-08-02 已完成模板可行性探索，方案已确认可行**。实现前请先与管理员确认方案，实施时直接按下方方案执行，无需重新探索。

### 增强 Lab 新闻栏（News）—— ✅ 已确认可行，纯内容方案

- **目标**：及时更新本 lab 相关的新消息（获奖、会议报告、媒体报道、成员动态等）
- **结论**：当前 Wowchemy Academic v5 的首页模块机制 = `content/{en,zh}/home/*.md` widget 文件 + `menus.yaml`/`menus.zh.yaml` 菜单项。模板自带 `pages` widget（现有 `posts.md` 正在使用），支持按文件夹过滤。**零模板代码改动**即可实现。
- **实施方案（推荐）**：
  1. 新建 `content/{en,zh}/news/` 内容文件夹存放新闻条目（格式同博客 `post/`）
  2. 新建 `content/{en,zh}/home/news.md`，front matter 用 `widget: pages` + `content.filters.folders: [news]`（参考现有 `posts.md` 的写法：`count: 5`、`order: desc`、`view: compact`）
  3. 在 `config/_default/menus.yaml` / `menus.zh.yaml` 加菜单项（如 `url: '#news'`，weight 设为 55，插在 Blog Posts 60 之前）
  4. 若只更新一种语言 → 加入 `.github/scripts/i18n_allowlist.txt` 豁免
- **注意**：仍须遵循 en/zh 双语同步规则；新闻条目复用 `news/` 文件夹后，`i18n_allowlist` / 同步检查自动覆盖

### 增加 Social Media 模块（X / Twitter feed）—— ✅ 已确认可行，blank widget 方案

- **目标**：将 PI 的 X（Twitter）账号 feed 显示在网站上
- **结论**：主题 `themes/github.com/wowchemy/wowchemy-hugo-themes/modules/wowchemy/v5/config.yaml` **已开启 `markup.goldmark.renderer.unsafe: true`**（raw HTML 允许渲染）→ 可直接把 X 官方嵌入代码放进 `blank` widget 正文，静态站 JS 客户端加载，Netlify 部署无问题。
- **实施方案（推荐）**：
  1. 在首页 `content/{en,zh}/home/` 新建 `xfeed.md`，front matter 用 `widget: blank`，正文粘贴 X 官方 timeline 嵌入代码：
     ```html
     <a class="twitter-timeline" href="https://twitter.com/hcp4715">Tweets by @hcp4715</a>
     <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
     ```
  2. 建议放首页底部（如 weight 85）或 Contact 区，避免拖慢首屏
  3. 现有 `contact.md` 已有 `icon: twitter` 关注链接（`https://twitter.com/hcp4715`），Follow 按钮已存在，可保留
- **注意**：
  - X 域名在国内访问会失败/加载慢，页面可能挂起；若在意可加懒加载或 `defer`
  - X feed 为英文内容 → 只需一份，把模块加入 `i18n_allowlist.txt` 豁免即可，不强制 en/zh 同步
  - 若需要自定义渲染，可仿照现有 `layouts/partials/widgets/portfolio.html`（本仓库已有自定义 widget override 先例）新建 `xfeed.html` partial

### 模板探索备忘（2026-08-02，避免重复探索）

- **widget 查找机制**：`layouts/partials/widget_page.html:103` → `widgets/%s.html` partial；站点级 override 目录为 `layouts/partials/widgets/`（已有 `portfolio.html` 先例）
- **可用内置 widget**：about / accomplishments / blank / contact / experience / featurette / featured / hero / pages / people / portfolio / slider / tag_cloud
- **`blank` widget** 渲染 `{{ $st.Content }}`（raw HTML 直接输出），适合嵌第三方代码
- **`pages` widget** 支持 `content.filters.folders` 过滤（现有 `posts.md` 用法：`folders: [post]`、`count`、`order: desc`、`view: compact`）
- **`contact` widget** 已支持 `contact_links`（twitter 图标示例见 `contact.md`）
- **`config.yaml`** 已设 `baseURL: https://chuan-peng-lab.netlify.app/`、`markup` 合并自主题（`_merge: deep`）

---

## 全局规则（所有任务强制）

- **en/zh 同步**：改任何内容，两种语言都要改（CI 校验）
- **YAML front matter**：值含冒号/特殊字符 → 双引号包裹
- **文件夹重命名**：用 `git mv` 保留历史；改文件夹名后检查 `projects:` 引用
- **提交规范**：PLAIN English 风格，如 "add new member xxx"、"mark xxx as Alumni"
- **验证**：改完跑 CI 脚本（见下）确认全绿再提交

## 常用命令

```bash
Rscript -e "blogdown::serve_site()"                     # 本地预览
Rscript -e "blogdown::build_site()"                     # 构建（注意 'public' 坑）
python3 .github/scripts/check_i18n_sync.py              # 中英同步检查
python3 .github/scripts/check_alumni.py                 # 校友一致性
python3 .github/scripts/mark_alumni.py <名字> --end "2026"  # 成员离组
/tmp/opencode/ci-venv/bin/python .github/scripts/validate_frontmatter.py  # front matter 校验（需 PyYAML 的 venv；系统 python3 无 yaml 模块）
```

## 已知坑

- **`'public'` 垃圾目录**：经 Rscript（非 RStudio）跑 `blogdown::build_site()` 会在根目录生成名字含引号的 `'public'` 目录（blogdown 转义 `-d 'public'` 参数，system2 不经 shell 传引号给 hugo）。删除：`rm -rf "'public'"`
- **`public/` 是构建产物**（gitignored），不要提交
- **`.sisyphus/`** 是工作文件（gitignored）
- **系统 python3 无 PyYAML**：跑 validate_frontmatter 需用 venv（`/tmp/opencode/ci-venv`）或 `pip install pyyaml`
- **Crossref 查询**注意限速（间隔 ≥0.5s）和 404（中文期刊/预印本多无记录）
