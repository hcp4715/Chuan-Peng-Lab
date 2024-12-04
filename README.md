
## Baisc Usage

Clone this repo, and run below code in R: 
- `blogdown:::serve_site()` run serve at local host
- `blogdown:::new_post_addin()` add new posts. 
- `blogdown::build_site()` build the site. 
- After that, you can commit the change and push it to github.

---

## Custom Setting
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
<!-- How to update introduction of the lab
孟真，你能在这里把详细的步骤写一下吗？
-->

<!-- How to update team members's info
孟真，你能在这里把详细的步骤写一下吗？
-->

<!-- How to add new Chinese publication:
孟真，你能在这里把详细的步骤写一下吗？
-->

<!-- How to add new English publication:
孟真，你能在这里把详细的步骤写一下吗？
-->