import markdown
from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
import logging
from django.utils import timezone
from django.shortcuts import redirect
from .models import Post,Comment,Category
from .forms import PostForm,CommentForm

# Create your views here.
def post_list(request):
    #posts=Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    posts=Post.objects.all().order_by('published_date')
    print(posts)
    return render(request,'blog/post_list.html',{'posts':posts})

def post_detail(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.increase_views()
    post.text = markdown.markdown(post.text,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                      ])
    return render(request,'blog/post_detail.html',{'post':post})

@login_required
def post_new(request):
    if request.method == 'POST':
        form=PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail',pk=post.pk)
    else:
        form=PostForm()
    return render(request,'blog/post_edit.html',{'form':form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    print(str(request.method))
    if request.method == 'POST':
        print('aa')
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            #return redirect('blog.views.post_detail', pk=post.pk)
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    print(posts)
    return render(request, 'blog/post_draft_list.html',{'posts':posts})


@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    print(request.method)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post=post
            comment.save()
            return redirect('post_detail',pk=post.pk)
    else:
        form=CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)

def archives(request, year ,month):
    posts = Post.objects.filter(created_date__year=year,
                                    created_date__month=month
                                    ).order_by('created_date')
    return render(request,'blog/post_list.html',{'posts':posts})

def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    posts= Post.objects.filter(category=cate).order_by('-created_date')
    return render(request, 'blog/post_list.html', context={'posts':posts})
