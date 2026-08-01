---
# 新博客模板
# 用法：填写本文件后运行
#   python .github/scripts/add_post.py templates/new_post.md
# 脚本将创建 content/{en,zh}/post/{日期-标题}/index.md。
title: 我的文章标题          # 博客标题（en/zh 默认相同，生成后可分别修改）
date: "2026-08-01"         # 日期 YYYY-MM-DD（用于文件夹名和 front matter）
summary: 文章简介
tags:
  - 标签1
bilingual: true            # true=同时创建 en/zh；false=只建英文版并自动加入 i18n 豁免名单
---

正文内容（Markdown）... 生成后 en/zh 默认相同，可按语言分别修改。
