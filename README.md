
## Baisc Usage

Clone this repo, and run below code in R: 
- `blogdown:::serve_site()` run serve at local host
- `blogdown:::new_post_addin()` add new posts. 
- `blogdown::build_site()` build the site. 
- After that, you can commit the change and push it to github.

---

## Files and folders for custom settings (个体化/修改网站内容可以改动的地方)
```
config\_default: 
	config.yaml
		title: Chuan-Peng Lab # Website name
		baseURL: 'https://chuan-peng-lab.netlify.app/' # Website URL 
	menus.yaml / menus_zh.yaml
		name, url, weight
	params.yaml
		appearance:
			theme_day: minimal
			theme_night: minimal

content\en(zh)
	authors: Home
	home: chunks in the home page
		demo: greenn -> blue
		skills: research fields
		projects: team
		publications: featured
		collaborators: accomplishments
		posts: blog posts
		contact: contact
		demo_join_us: join us
	post: blog posts
	project: informations of team members
	publication: 
		index.md: title, abstract, publication date... [fill in all the information here]
		cite.bib: copy from Google Scholar
		featured.jpg: pic in paper


static
	To insert an image, please place the image here.

no need editing other folders
```

英文版在content\en\
中文版在content\zh\
修改某个地方后, 在R的console里输入blogdown::serve_site()检查是否可以正常运行
如果可以正常渲染网站, 那么再输入blogdown::build_site(), 最后上传至GitHub
如果发现可以正常运行, 但是修改内容没有实装. 
	1. 那么可以运行blogdown::stop_site()后, 再输入blogdown::serve_site()
	2. 或关闭R studio重新打开. 

## To modify the introduction of the website
"content\en\authors\admin\"
该文件夹下的_index.md就是introduction

	"---" 分割线上面部分, 在对应地方填写对应内容 
	"---" 分割线下方部分, 符合html语法的都可以正常显示

## To update team members's info
Path: "content\en\project\" \
该文件夹下每个子文件夹代表一个成员的信息，文件夹名是姓名缩写. 

### 修改
	打开一个人的个人信息, 修改`index.md`
	featured.jpg是该人员头像
### 创建
	复制任意一个人的文件夹并修改为目标人员的名字
	在复制的文件夹内修改`index.md`和`featured.jpg`

## To update publications
Path for 英文: `content\en\publication\` \
Path for 中文: `content\zh\publication\`

1. 复制任意一个已存在的文件夹
2. 修改`cite.bib`, 该内容可以在Google scholar上复制得到或者在Zotero上生成后复制
3. 修改`featured.jpg`, 可以使用该文章内的任意一张图片
4. 修改`index.md` (没有提到的可以不改) \
	abstract: 这部分直接复制文章的摘要. **但是注意不能有冒号** \
	author_notes: 代表作者右上角的上标. 可以不写 \
	authors: 作者的名字 \
	date: 按照现有格式修改时间 \
	doi: 正常填写doi \
	featured: 表示这张图片是否显示在主页预览中. 只有true会显示在主页上. false意味着显示在更多中 \
	publication: 期刊 \
	publication_short: 期刊的缩写名字. 也可以填全名 \
	publication_types: 不同的数字代表发表方式, 1=会议文章, 2 = 期刊, 3 = preprint \
	summary: 显示在主页上的缩略介绍. 一般选择摘要的第一句话 \
	title: 标题

	"---" 分割线下方部分, 
	“Click the _Preprint_ button below abstract to check all other Preprint in the website.”
	注意这句话与上面的publication_types一致就行
	
	