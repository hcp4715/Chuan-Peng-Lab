---
# 新论文模板
# 用法：填写本文件后运行
#   python .github/scripts/add_publication.py templates/new_publication.md
# 脚本将自动：
#   1. 用 DOI 查询 Crossref，补全卷期号/年份，并校验标题是否匹配
#   2. 生成 content/{en,zh}/publication/{年份}_{类型}_{作者}/ 的 index.md 和 cite.bib
title: "How sleeping minds decide: State-specific reconfigurations of lexical decision-making"
title_zh: ""               # 中文标题（可选，留空则 en/zh 用同一标题）
type: journal              # journal（期刊）/ preprint（预印本）
authors:
  - "Xia, Tao"
  - "Hu, Chuan-Peng"
  - "Türker, Basak"
journal: PLOS Computational Biology   # 期刊名（preprint 填平台名，如 PsyArXiv）
year: 2026                 # 发表年份
doi: "10.1371/journal.pcbi.1014007"   # 可选；有则自动查 Crossref 补全元数据
url_source: ""             # 预印本平台链接（可选；preprint 建议填写）
abstract: ""               # 可选；留空则尝试从 Crossref 自动拉取
---

（本模板正文留空即可。摘要自动从 Crossref 获取，或在上方 abstract 字段填写。）
