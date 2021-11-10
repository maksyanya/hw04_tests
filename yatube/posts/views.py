
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.core.paginator import Paginator

from posts.forms import PostForm
from posts.models import Group
from posts.models import Post
from posts.models import User

POSTS_QTY = 10


def get_page(request, posts):
    paginator = Paginator(posts, POSTS_QTY)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    return render(request, 'posts/index.html', context={
        'page_obj': get_page(request, Post.objects.all()),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', context={
        'page_obj': get_page(request, group.posts.all()),
        'group': group,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = get_page(request, posts)
    context = {
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=post.author.username)


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect(
            'posts:post_detail',
            post_id=post.id
        )
    form = PostForm(request.POST or None, instance=post)
    if not form.is_valid():
        context = {
            'post': post,
            'form': form,
            'is_edit': True
        }
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect(
        'posts:post_detail',
        post_id=post.id
    )
