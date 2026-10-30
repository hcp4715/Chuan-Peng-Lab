# FuturePlan.md — 传鹏实验室网站：规划中的功能

**状态**：方案已验证，**尚未实现**
**最后更新**：2026-08-02（完成模板可行性探索）
**姊妹文档**：[AGENTS.md](AGENTS.md) —— 成员更新网站内容的操作指南

本文件只收录**尚未实现**的功能增强，不属于日常维护职责。日常更新成员、论文、博客，请只看 [AGENTS.md](AGENTS.md)。

实现前请先与管理员确认方案；确认后直接按下方方案执行，无需重新探索。

---

## 1. 增强 Lab 新闻栏（News）—— ✅ 已确认可行，纯内容方案

**目标**：及时更新本 lab 相关的新消息（获奖、会议报告、媒体报道、成员动态等）。

**结论**：Wowchemy Academic v5 的首页模块 = `content/{en,zh}/home/*.md` widget 文件 + `menus.yaml` / `menus.zh.yaml` 菜单项。模板自带 `pages` widget（现有 `posts.md` 就在用），支持按文件夹过滤，**零模板代码改动**即可实现。

**实施方案**：

1. 新建 `content/{en,zh}/news/` 内容文件夹存放新闻条目（格式同博客 `post/`）
2. 新建 `content/{en,zh}/home/news.md`，front matter 用 `widget: pages` + `content.filters.folders: [news]`（参考 `posts.md`：`count: 5`、`order: desc`、`view: compact`）
3. 在 `config/_default/menus.yaml` / `menus.zh.yaml` 加菜单项（如 `url: '#news'`，weight 55，插在 Blog Posts 60 之前）
4. **必做**：把 `"news"` 加进 `.github/scripts/check_i18n_sync.py` 的 `SECTIONS`（当前为 `["project", "publication", "post"]`）。不加的话，新目录**完全不在**中英同步检查范围内，只建一侧语言也不会被 CI 发现。

**注意**：

- 仍需遵循 en/zh 双语规则；只建单语条目时，按 `[EN only] news/xxx` / `[ZH only] news/xxx` 的格式登记到 `.github/scripts/i18n_allowlist.txt`
- `home/` 目录目前不在同步检查范围内，首页 widget 不受双语检查约束

## 2. 增加 Social Media 模块（X / Twitter feed）—— ✅ 已确认可行，blank widget 方案

**目标**：把 PI 的 X（Twitter）账号 feed 显示在网站上。

**结论**：主题 `themes/github.com/wowchemy/wowchemy-hugo-themes/modules/wowchemy/v5/config.yaml` 已开启 `markup.goldmark.renderer.unsafe: true`（允许 raw HTML）→ 可直接把 X 官方嵌入代码放进 `blank` widget 正文，静态站由 JS 客户端加载，Netlify 部署无问题。

**实施方案**：

1. 在 `content/{en,zh}/home/` 新建 `xfeed.md`，front matter 用 `widget: blank`，正文粘贴官方 timeline 代码：

   ```html
   <a class="twitter-timeline" href="https://twitter.com/hcp4715">Tweets by @hcp4715</a>
   <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
   ```

2. 建议放首页底部（如 weight 85）或 Contact 区，避免拖慢首屏
3. 现有 `contact.md` 已有 `icon: twitter` 关注链接（`https://twitter.com/hcp4715`），Follow 按钮已存在，可保留

**注意**：

- X 域名在国内访问会失败或加载很慢，页面可能挂起；在意的话加懒加载或 `defer`
- `home/` 不在 i18n 同步检查范围内，只需一份英文模块，**不需要**加 allowlist（加了也不会被匹配）
- 需要自定义渲染时，可仿照现有 `layouts/partials/widgets/portfolio.html`（本站已有自定义 widget override 先例）新建 `xfeed.html` partial

---

## 附录：模板探索备忘（2026-08-02，避免重复探索）

- **widget 查找机制**：`layouts/partials/widget_page.html` 把 widget 解析为 `widgets/{name}.html` partial；站点级 override 目录为 `layouts/partials/widgets/`（已有 `portfolio.html` 先例）
- **可用内置 widget**：about / accomplishments / blank / contact / experience / featurette / featured / hero / pages / people / portfolio / slider / tag_cloud
- **`blank` widget** 渲染 `{{ $st.Content }}`（raw HTML 直接输出），适合嵌第三方代码
- **`pages` widget** 支持 `content.filters.folders` 过滤（`posts.md` 用法：`folders: [post]`、`count`、`order: desc`、`view: compact`）
- **`contact` widget** 支持 `contact_links`（twitter 图标示例见 `contact.md`）
- **`config.yaml`** 已设 `baseURL: https://chuan-peng-lab.netlify.app/`，`markup` 配置自主题合并（`_merge: deep`）

---

## 本文件的维护约定

- 新规划**追加到末尾**，每条注明验证日期与结论，避免重复探索
- 某条实现完成后，从本文件删除，并在 [AGENTS.md](AGENTS.md) 补上对应操作步骤
- 本文件不是操作指南；不要在这里写任何"当前该怎么做"的规则
