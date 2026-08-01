# 传鹏实验室网站

> 网站地址：https://chuan-peng-lab.netlify.app/ or https://huchuanpeng.com/

---

## 目录

- [一、基本信息](#一基本信息)
  - [快速入门](#快速入门)
  - [技术栈](#技术栈)
  - [文件结构概览](#文件结构概览)
  - [环境配置](#环境配置)
  - [部署原理](#部署原理)
  - [其他资源](#其他资源)
- [二、快速导航（操作速查表）](#二快速导航操作速查表)
- [三、内容更新](#三内容更新)
  - [Git 协作流程](#git-协作流程)
  - [成员信息变更](#成员信息变更)
  - [论文信息变更](#论文信息变更)
    - [添加新论文](#添加新论文)
    - [`projects` 字段](#projects-字段)
    - [论文类型](#论文类型)
    - [论文从预印本转为正式发表](#论文从预印本转为正式发表)
  - [添加博客文章](#添加博客文章)
  - [中英文内容同步](#中英文内容同步)
  - [检查清单](#检查清单)
- [四、站点维护（管理员）](#四站点维护管理员)
  - [修改网站简介](#修改网站简介)
  - [修改导航菜单与站点配置](#修改导航菜单与站点配置)
  - [从 BibTeX 批量导入论文](#从-bibtex-批量导入论文)
- [五、常见问题](#五常见问题)

---

## 一、基本信息

### 快速入门

1. 克隆本仓库
2. 在 R 控制台运行 `blogdown::serve_site()` 本地预览
3. 编辑 `content/en/`（英文）或 `content/zh/`（中文）中的文件
4. 运行 `blogdown::build_site()` 构建网站
5. 提交并推送到 GitHub，Netlify 会自动构建部署

> 🤖 **新成员可以用 AI 自动更新**：本仓库的 `AGENTS.md` 是给 AI 助手的维护指南。你可以直接让 AI 助手（Claude、ChatGPT 等）读取 `AGENTS.md`，然后按下方各任务的模板（`templates/` 提交区）帮你自动完成成员/论文/博客的更新——只需提供信息，AI 会填模板、跑脚本、生成中英文内容。

### 技术栈

| 组件 | 说明 |
|---|---|
| Hugo | 静态站点生成器，版本由 `netlify.toml` 固定为 v0.102.3 |
| blogdown | R 包，本地预览/构建工作流（`.Rproj` 项目） |
| Wowchemy Academic | v5 主题（`themes/github.com/wowchemy/...`） |
| Netlify | 网站托管与自动部署 |
| GitHub Actions | CI 自动检查（front matter 校验、中英同步检查） |
| R + Git | 开发环境前置条件 |

网站为**双语**（英文 `content/en/` + 中文 `content/zh/`），所有内容需在两种语言下同步维护。

### 文件结构概览

```
config/_default/
  config.yaml      # 网站标题、地址、模块
  languages.yaml   # 语言配置
  menus.yaml       # 导航菜单（英文）
  menus.zh.yaml    # 导航菜单（中文）
  params.yaml      # 主题设置

content/
  en/              # 英文内容
    authors/admin/ # PI 介绍
    home/          # 首页模块
    post/          # 博客文章
    project/       # 团队成员
    publication/   # 发表论文
  zh/              # 中文内容（结构与 en/ 完全一致，需同步维护）

static/            # 静态文件（图片等）
to_be_added_pubs/  # 待添加论文的 BibTeX 暂存区（已被 git 忽略）
.github/           # CI 自动化检查（front matter 校验、中英同步检查）
```

> **注意**：`content/en/` 与 `content/zh/` 内部结构完全一致，修改任何内容时两边都要改。

### 环境配置

#### 前置条件
- 已安装 R 和 RStudio
- 已安装 Git

#### 安装 blogdown
```r
install.packages("blogdown")
blogdown::install_hugo()
```

#### 本地预览
```r
blogdown::serve_site()   # 启动本地服务器
blogdown::stop_site()    # 停止服务器
blogdown::build_site()   # 构建网站
```

如果修改未生效：
1. 运行 `blogdown::stop_site()`，再运行 `blogdown::serve_site()`
2. 或重启 RStudio

### 部署原理

- 网站托管在 **Netlify**，与 GitHub 仓库关联
- **推送到 `main` 分支后，Netlify 自动构建并部署**，一般需要 1~2 分钟
- 本地修改后如果网站没变化，先确认：① 是否已经 `git push`；② 是否推送到了正确的分支；③ Netlify 后台构建是否成功
- Netlify 构建命令见 `netlify.toml`（`hugo` 构建，输出到 `public/`）
- `public/` 是构建产物，已被 git 忽略，**不要手动提交**

### 其他资源

- [Wowchemy 文档](https://wowchemy.com/docs/)
- [blogdown 书籍](https://bookdown.org/yihui/blogdown/)
- [Hugo 文档](https://gohugo.io/documentation/)

---

## 二、快速导航（操作速查表）

| 想做什么 | 操作位置 | 关键步骤 |
|---|---|---|
| 添加新成员 | `content/{en,zh}/project/{姓名全拼}/` | 复制现有成员文件夹 → 改 `index.md` → 换 `featured.jpg` 头像 |
| 编辑成员信息 | `content/{en,zh}/project/{姓名全拼}/index.md` | 改 `tags`（角色）与 `summary` |
| 成员离组 | 同上 | `tags` 改为 `Alumni`，更新 `summary` 时间范围 |
| 添加新论文 | `content/{en,zh}/publication/{年份_Publication_作者}/` | 建文件夹 → 写 `cite.bib` + `index.md` |
| 预印本转正式发表 | 见[论文从预印本转为正式发表](#论文从预印本转为正式发表) | 新建正式版 → 删除预印本 |
| 添加博客文章 | `content/{en,zh}/post/{日期-标题}/` | 建文件夹 → 写 `index.md` |
| 修改简介 | `content/{en,zh}/authors/admin/_index.md` | 直接编辑 |
| 修改导航菜单 | `config/_default/menus.yaml` + `menus.zh.yaml` | 编辑并本地预览 |

> **中英文都要改**：本网站是双语的，所有内容需要在 `content/en/` 和 `content/zh/` 各维护一份（详见[中英文内容同步](#中英文内容同步)）。

---

## 三、内容更新

### Git 协作流程

本仓库使用 **Fork + Pull Request** 的协作模式。实验室成员（尤其是非技术背景的同学）请按以下步骤操作：

1. **Fork 仓库**：在 GitHub 网页打开 `github.com/hcp4715/Chuan-Peng-Lab`，点击右上角 `Fork`
2. **克隆自己的仓库**：
   ```bash
   git clone git@github.com:{你的用户名}/Chuan-Peng-Lab.git
   cd Chuan-Peng-Lab
   ```
3. **创建新分支**（建议用描述性的名字）：
   ```bash
   git checkout -b add-chen-xx
   ```
4. **修改内容文件**（参见本节下方各小节说明）
5. **提交并推送**：
   ```bash
   git add .
   git commit -m "添加成员陈某某"
   git push origin add-chen-xx
   ```
6. **发起 Pull Request**：在 GitHub 网页进入你的仓库，点击 `Compare & pull request`，填写说明后提交。管理员审核合并后，网站会自动更新

> 管理员（PI）可以直接在 main 分支上修改，也可以合并成员提交的 PR。

### 成员信息变更

> 💡 **AI 自动更新（推荐新成员使用）**：你可以直接让 AI 助手完成整个流程——AI 会读取仓库里的 `AGENTS.md` 维护指南、按照 `templates/member/_template.md` 的格式填写你的信息、运行 `python .github/scripts/add_member.py templates/member/` 自动生成中英文页面。你只需告诉 AI 你的姓名、角色和简介（以及一张头像图片）即可。也可以手动把填写好的信息放入 `templates/member/` 提交区。

#### 文件路径
- 英文：`content/en/project/{姓名全拼}/index.md`
- 中文：`content/zh/project/{姓名全拼}/index.md`
- 头像：`content/en/project/{姓名全拼}/featured.jpg`

> `{姓名全拼}` 即姓+名拼音拼接、各音节首字母大写，如 `HuangYijie`、`HuChuanpeng`

#### 角色标签
| 标签 | 说明 |
|-----|------|
| `Principal Investigator` | 实验室负责人 |
| `Research Assistants` | 研究助理 |
| `Postgraduate` | 研究生 |
| `Undergraduate` | 本科生 |
| `Alumni` | 已毕业成员 |

#### 添加新成员

1. **创建文件夹**
   - 复制一个现有成员的文件夹
   - 重命名为新成员的姓名全拼（姓+名拼接、首字母大写，如 `HuangYijie`）

2. **编辑 `index.md`**
   ```yaml
   ---
   date: "2024-09-01T00:00:00Z"
   image:
     caption: 你的名字
     focal_point: Smart
   links:
   - icon: github
     icon_pack: fab
     name: Follow
     url: https://github.com/你的用户名
   summary: __2024年9月 ~ 至今__ <br/> 简短介绍
   tags:
   - Undergraduate        # 从上方角色标签中选择
   title: 你的名字
   ---
   在这里写个人简介，支持 Markdown 和 HTML。
   ```

3. **添加头像**
   - 替换 `featured.jpg`（建议大小 < 500KB）

4. **英文和中文版本都要添加**

#### 编辑现有成员
- 打开成员文件夹中的 `index.md`
- 根据需要更新字段
- 运行 `blogdown::serve_site()` 预览

#### 成员离组

**推荐使用自动脚本**（一键更新中英文的 `tags` 和 `summary` 时间范围）：

```bash
python .github/scripts/mark_alumni.py <姓名全拼>... --end "2026"
```

例如：

```bash
python .github/scripts/mark_alumni.py wjq zrz zss --end "2026"
```

- 脚本会同时更新 `content/en/project/` 和 `content/zh/project/` 下的文件：`tags` 改为 `Alumni`，`summary` 时间范围由 `__Sep. 2023 ~ Now__` 改为 `__Sep. 2023 ~ 2026__`
- `--start` 可省略（自动读取现有起始时间）；加 `--dry-run` 可先预览而不写入

脚本不涉及的内容，需手动检查：
- 正文中的"在读"等时效性信息
- 进行中项目的关联信息
- 用 `blogdown::serve_site()` 预览，提交推送（CI 会校验所有 Alumni 成员已填写结束时间、中英文一致）

### 论文信息变更

> 💡 **AI 自动更新（推荐）**：只需给 AI 提供论文标题、作者和 DOI（或直接给 BibTeX），AI 会按照 `templates/publication/_template.md` 的格式填写并运行 `python .github/scripts/add_publication.py templates/publication/`，自动生成中英文论文页（包括用 Crossref 自动补全卷期号、年份和摘要）。也可手动把填写好的模板放入 `templates/publication/` 提交区。

#### 文件路径
- 英文：`content/en/publication/{年份_Publication_第一作者}/`
- 中文：`content/zh/publication/{年份_Publication_第一作者}/`

每个论文文件夹包含：
- `index.md` - 论文元数据
- `cite.bib` - BibTeX 引用
- `featured.jpg` - 预览图片（可选）

#### 添加新论文

1. **创建文件夹**
   - 复制一个现有论文文件夹
   - 重命名为 `{年份}_Publication_{第一作者}`（如 `2024_Publication_Andres`）

2. **编辑 `cite.bib`**
   - 从 Google Scholar 或 Zotero 复制 BibTeX

3. **编辑 `index.md`**

   关键字段：
   ```yaml
   ---
   abstract: "论文摘要（含冒号时务必用双引号包裹，见常见问题）"
   authors:
   - 第一作者
   - 第二作者
   date: "2024-03-27T00:00:00Z"
   doi: "10.xxxx/xxxxx"
   featured: false        # 是否在主页显示
   projects:
   - csy                  # 关联成员/项目标识符，可选，如不需要留空 ""
   publication: In *Journal Name*
   publication_short: In *J. Name*
   publication_types:
   - "2"                  # 期刊文章；编号含义见"论文类型"表
   summary: 主页显示的简介
   title: 论文标题
   url_pdf: "https://..."  # PDF 链接，可选
   ---
   ```

4. **添加预览图片**（可选）
   - 用论文中的图片替换 `featured.jpg`

5. **中文版同样操作**

#### `projects` 字段

`projects` 字段用于将论文与相关项目或成员关联。

- **用途**：将论文与特定项目/成员页面关联
- **格式**：项目标识符列表（对应 `content/{en,zh}/project/` 下的文件夹名）
- **示例**：
  ```yaml
  projects:
  - csy
  ```
- **注意**：这是可选的。如不需要可留空（`projects: ""`）

#### 论文类型

> **注意**：编号由主题固定（`themes/github.com/wowchemy/wowchemy-hugo-themes/modules/wowchemy/v5/data/publication_types.toml`），填写其他编号会导致标签显示错误。

| 值 | 类型（英文） | 类型（中文） |
|-------|------|------|
| `"1"` | Conference paper | 会议文章 |
| `"2"` | Journal article | 期刊文章 |
| `"3"` | Preprint | 预印本 |
| `"4"` | Report | 报告 |
| `"5"` | Book | 书籍 |
| `"6"` | Book section | 章节 |
| `"7"` | Thesis | 论文 |
| `"8"` | Patent | 专利 |

> 书或章节使用 `"5"`（书籍）或 `"6"`（章节）。

#### 论文从预印本转为正式发表

当预印本（Preprint）被期刊正式接收发表后，把网站上的预印本条目替换为正式发表条目（例如 `2024_Preprint_Duan` → `2024_Publication_Duan`）：

1. **创建正式发表文件夹**：`content/{en,zh}/publication/{年份}_Publication_{第一作者}/`（可复制原预印本文件夹）
2. **更新元数据**：
   - `title`、`abstract` 改为正式版内容
   - `publication` / `publication_short` 填写期刊名
   - `doi` 填写正式 DOI
   - `publication_types` 从 `"3"`（预印本）改为 `"2"`（期刊文章）
   - 补充 `url_pdf`、`url_code` 等链接
3. **删除预印本文件夹**：`content/{en,zh}/publication/{年份}_Preprint_{第一作者}/`
4. **中英文都要操作**（步骤 1-3 在 `content/en/` 和 `content/zh/` 各做一遍）
5. 本地预览确认，提交推送，CI 通过后自动部署

### 添加博客文章

> 💡 **AI 自动更新（推荐）**：把文章标题、摘要和正文告诉 AI，AI 会按照 `templates/post/_template.md` 的格式填写并运行 `python .github/scripts/add_post.py templates/post/` 自动创建中英文文章页。也可手动把写好的文章放入 `templates/post/` 提交区。

#### 文件路径
- 英文：`content/en/post/{日期-标题}/index.md`
- 中文：`content/zh/post/{日期-标题}/index.md`

> 旧文章也可以直接放在 `content/{en,zh}/post/` 下（如 `2019-04-29-how-to-install-and-use-hddm.md`）

#### 步骤
1. **创建文件夹**：`content/en/post/2026-08-01-my-post/`
2. **编辑 `index.md`**：
   ```yaml
   ---
   title: 我的文章标题
   date: "2026-08-01T00:00:00Z"
   summary: 文章简介
   tags:
   - 标签1
   ---
   正文内容，支持 Markdown。
   ```
3. **中英文都要添加**（英文版 `index.md`，中文版同样结构）
   - **如果文章不需要中英同步**（如仅面向国内读者的中文教程），则不必创建另一种语言版本，但**必须将差异加入 CI 豁免名单** `.github/scripts/i18n_allowlist.txt`，否则中英同步检查会标红：
     ```
     [ZH only] post/2026-08-01-my-post
     ```
   - 格式为脚本输出样式（`[EN only]` / `[ZH only]` + 相对路径），一行一条；日后补齐双语后请移出该行
4. 本地预览确认后提交推送

### 中英文内容同步

网站是双语的，`content/en/` 与 `content/zh/` 必须保持同步，否则会出现一种语言有、另一种语言没有的情况。

#### 手动检查
在项目根目录运行：
```bash
# 对比论文目录
diff <(ls content/en/publication) <(ls content/zh/publication)

# 对比成员目录
diff <(ls content/en/project) <(ls content/zh/project)
```
有输出即表示存在差异，需要补齐。

#### 自动检查（CI）
仓库已配置 GitHub Actions（`.github/workflows/check-content.yml`），每次推送和 PR 时自动执行：

1. **Front matter 校验**：检查所有 `content/` 下的文件 front matter 是否能正确解析（YAML/TOML）
2. **中英文同步检查**：对比 `project`、`publication`、`post` 三个目录，发现差异时 CI 会变红

已知暂不同步的内容可通过 `.github/scripts/i18n_allowlist.txt` 豁免；补齐后请移出该文件。

> CI 变红时查看 GitHub 仓库页面的 `Actions` 标签查看具体错误。

### 检查清单

#### 新成员加入
- [ ] 在 `content/en/project/{姓名全拼}/` 创建文件夹
- [ ] 在 `content/zh/project/{姓名全拼}/` 创建文件夹
- [ ] 编辑 `index.md`（英文和中文）
- [ ] 添加 `featured.jpg` 头像
- [ ] 设置正确的角色标签
- [ ] 用 `blogdown::serve_site()` 预览
- [ ] 用 `blogdown::build_site()` 构建
- [ ] 提交并推送到 GitHub（提 PR 或直接推 main）

#### 新论文发表
- [ ] 在 `content/en/publication/{年份_Publication_第一作者}/` 创建文件夹
- [ ] 在 `content/zh/publication/{年份_Publication_第一作者}/` 创建文件夹
- [ ] 编辑 `cite.bib`
- [ ] 编辑 `index.md`（英文和中文）
- [ ] `abstract` 含冒号时已加引号
- [ ] 添加 `featured.jpg`（可选）
- [ ] 设置正确的 `publication_types`
- [ ] 用 `blogdown::serve_site()` 预览
- [ ] 用 `blogdown::build_site()` 构建
- [ ] 提交并推送到 GitHub

#### 成员离组
- [ ] 运行 `python .github/scripts/mark_alumni.py {姓名全拼} --end "2026"`（或手动改 `tags` 和 `summary`）
- [ ] 更新正文中"在读"等时效性信息
- [ ] 更新进行中项目的信息
- [ ] 预览并确认
- [ ] 提交并推送到 GitHub

---

## 四、站点维护（管理员）

### 修改网站简介

PI 介绍位于：
- `content/en/authors/admin/_index.md`
- `content/zh/authors/admin/_index.md`

直接编辑文件即可。`---` 分隔线下方支持 HTML。

### 修改导航菜单与站点配置

#### 导航菜单
- 英文：`config/_default/menus.yaml`
- 中文：`config/_default/menus.zh.yaml`

菜单项通过 `url` 指向首页的某个模块（`#` + 模块文件名）：
```yaml
main:
  - name: 首页
    url: '#about'       # 指向 content/{lang}/home/about.md
    weight: 10          # 数值越小越靠前
  - name: 团队
    url: '#project'
    weight: 30
```
新增首页模块后，如果需要显示在导航里，在这里加一项即可。

#### 其他站点配置
| 文件 | 用途 |
|---|---|
| `config/_default/config.yaml` | 网站标题、baseURL、Hugo 模块 |
| `config/_default/languages.yaml` | 语言设置 |
| `config/_default/params.yaml` | 外观主题、统计代码、SEO |

> 修改配置后必须重新构建才能生效，建议先本地预览确认。

### 从 BibTeX 批量导入论文

`to_be_added_pubs/` 目录存放待添加论文的 BibTeX 文件（已被 git 忽略）。如需批量导入，可使用 [hugo-academic-cli](https://github.com/wowchemy/hugo-academic-cli)：

```bash
academic import --bibtex "to_be_added_pubs/Exported Items.bib" --content-dir content/en/publication
```

> 导入后仍需手动检查/补充 `index.md` 中的字段（`abstract`、`summary`、`publication_types` 等），并同步创建中文版。该工具已停止维护，导入结果以手动核对为准。

---

## 五、常见问题

### 修改后网站未更新
1. 检查是否已 `git push` 到 `main` 分支（详见[部署原理](#部署原理)）
2. 本地预览问题：停止服务器 `blogdown::stop_site()` → 重新启动 `blogdown::serve_site()`
3. 如仍无效，重启 RStudio

### YAML 解析错误（构建失败最常见原因）
这是最容易踩的坑。**如果 `abstract`（或任何字段）的值里包含冒号 `:`，必须用双引号包裹**：

```yaml
# 错误写法（值里的 "i.e.," 带冒号会导致解析失败）
abstract: Social evaluation, i.e., how people judge others...

# 正确写法
abstract: "Social evaluation, i.e., how people judge others..."
```

- 检查 `abstract` 字段是否有冒号
- 确保缩进正确
- 含特殊字符的值用引号包裹
- CI 的 front matter 校验（`.github/workflows/check-content.yml`）可以在部署前发现此类问题

### 图片不显示
- 检查文件路径是否正确
- 新图片放在 `static/` 文件夹
- 在 markdown 中引用为 `/img/filename.jpg`

### 中英文不同步
- 参考[中英文内容同步](#中英文内容同步)一节对比两个目录
- CI 的同步检查会标红提示

### 文件夹名冲突
如果两人姓名全拼相同（重名）：
- 添加数字后缀：`HuChuanpeng`、`HuChuanpeng2`

### 构建后出现名为 `'public'` 的目录
通过 Rscript（非 RStudio 交互会话）运行 `blogdown::build_site()` 时，blogdown 会把输出目录名转义为 `-d 'public'`，经 `system2` 传给 hugo 时引号未被剥离，导致生成一个**名字含单引号**的 `'public'` 目录。它与正常构建产物 `public/` 内容重复，是垃圾目录，直接删除即可：

```bash
rm -rf "'public'"
```

- 它是未跟踪目录（不被 `public/` 忽略规则匹配），会在 `git status` 显示为 `?? 'public'/`
- 建议日常构建使用 RStudio 的 `blogdown::serve_site()` / `build_site()`，可避免此问题

---

*最后更新：2026年8月*
