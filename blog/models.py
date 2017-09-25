from __future__ import unicode_literals
import markdown
from django.utils.html import strip_tags

from django.db import models
from django.urls import reverse
from django.utils import timezone

# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    text = models.TextField()
    excerpt = models.CharField(max_length=200,blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True,null=True)
    excerpt = models.CharField(max_length=200,blank=True)
    category = models.ForeignKey(Category,null=True)
    tags = models.ManyToManyField(Tag, blank = True)
    views = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.excerpt:
            md=markdown.Markdown(extentions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                ])
            self.excerpt = strip_tags(md.convert(self.text))[:54]
        super(Post, self).save(*args, **kwargs)


    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk':self.pk})

    def __str__(self):
        return self.title

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

class Comment(models.Model):
    post = models.ForeignKey('blog.Post', related_name='comments')
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)
    
    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)
