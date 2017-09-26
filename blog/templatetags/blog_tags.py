from ..models import Post,Category,Tag
from django import template
from django.db.models.aggregates import Count

register = template.Library()

@register.simple_tag
def get_recent_posts(num=5):
    return Post.objects.all().order_by('-created_date')[:num]


@register.simple_tag
def archives():
    return Post.objects.dates('created_date','month',order='DESC')

@register.simple_tag
def get_categories():
    #return Category.objects.annotate(num_posts=Count('post')).filter(num_post__gt==0)
    return Category.objects.annotate(num_posts=Count('post'))

@register.simple_tag
def get_tags():
    #return Category.objects.annotate(num_posts=Count('post')).filter(num_post__gt==0)
    return Tag.objects.annotate(num_posts=Count('post'))
