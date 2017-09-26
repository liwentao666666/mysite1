import markdown
from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
import logging
from django.utils import timezone
from django.shortcuts import redirect
from .models import Post,Comment,Category,Tag
from .forms import PostForm,CommentForm
from django.views.generic import ListView,DetailView

# Create your views here.


class IndexView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name= 'posts'
    paginate_by=1

    def get_queryset(self):
        return super(IndexView,self).get_queryset().all().order_by('published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator, page, is_paginated)
        context.update(pagination_data)
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}

        left = []
        right=[]
        left_has_more = False
        right_has_more = False
        first = False
        last = False
        page_number= page.number
        total_pages = paginator.num_pages
        page_range = paginator.page_range
        if page_number==1:
            right = page_range[page_number:page_number + 2]

            if right[-1] < total_pages-1:
                right_has_more = True

            if right[-1]<total_pages:
                last = True

        elif page_number == total_pages:
            left = page_range[(page_number - 3) if (page_number-3)>0 else 0:page_number - 1]
            if left[0]>2:
                left_has_more = True

            if left[0]>1:
                first = True

        else:
            left = page_range[(page_number - 3 ) if (page_number -3)>0 else 0:page_number - 1 ]
            right = page_range[page_number:page_number + 2]
            if right[-1] < total_pages -1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            if left[0]>2:
                left_has_more = True
            if left[0]>1:
                first = True
        
        data = {
            'left':left,
            'right':right,
            'left_has_more':left_has_more,
            'right_has_more':right_has_more,
            'first':first,
            'last':last,
        }
        return data

class TagView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk = self.kwargs.get('pk'))
        return super(TagView,self).get_queryset().filter(tags=tag)


class CategoryView(ListView):
    model= Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        cate = get_object_or_404(Category, pk = self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate).order_by('-created_date')

class ArchivesView(ListView):
    model= Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return super(ArchivesView, self).get_queryset().filter(created_date__year=self.kwargs.get('year'),created_date__month=self.kwargs.get('month')).order_by('created_date')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self,request, *args, **kwargs):
        response= super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    def get_object(self,queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        post.body = markdown.markdown(post.body,
                                    extensions=[
                                        'markdown.extensions.extra',
                                        'markdown.extensions.codehilite',
                                        'markdown.extensions.toc',
                                        ])
        return post

    def get_context_data(self, **kwargs):
        context = super(PostDetailView,self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form':form,
            'comment_list':comment_list
        })
        return context

#def post_list(request):
#    #posts=Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
#    posts=Post.objects.all().order_by('published_date')
#    print(posts)
#    return render(request,'blog/post_list.html',{'posts':posts})

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

#def archives(request, year ,month):
#    posts = Post.objects.filter(created_date__year=year,
#                                    created_date__month=month
#                                    ).order_by('created_date')
#    return render(request,'blog/post_list.html',{'posts':posts})
#
#def category(request, pk):
#    cate = get_object_or_404(Category, pk=pk)
#    posts= Post.objects.filter(category=cate).order_by('-created_date')
#    return render(request, 'blog/post_list.html', context={'posts':posts})
