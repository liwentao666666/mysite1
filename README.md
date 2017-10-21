# mysite1
python version:3.5.2
django version:1.10.2

A django blog project for myself;
currently work on four functions:
1.list blogs
2.blog detail
3.create a blog
4.edit a blog


can use print with command:
python manage.py runserver --noreload 0.0.0.0:80

###########################################################
HOW to create category and tag?
>>> from blog.models import Category, Tag, Post
>>> c = Category(name='category test')
>>> c.save()
>>> t = Tag(name='tag test')
>>> t.save()
###########################################################

show full columns from blog_post_tags;
alter table blog_comment modify author varchar(200) character set utf8; 


#############################################
更改每页文章数:在blog/views.py中的 paginate_by参数
##################################################
