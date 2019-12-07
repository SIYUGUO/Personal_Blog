from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, JsonResponse
from users.models import Profile
from django.http import HttpResponseRedirect
# from django.contrib.postgres.search import (
#     SearchVector, SearchQuery, SearchRank
# )
from .models import Post
import re
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView,
    UpdateView,
    DeleteView,
    FormView
)
from .forms import SearchForm

# class SearchResultsView(ListView):
#     model = Post
#     template_name = 'douban/home.html'
#     context_object_name = 'posts'

#     ## SearchRank ##
#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         vector = SearchVector('content','title')
#         search_query = SearchQuery(query)
#         posts = Post.objects.annotate(
#             rank=SearchRank(vector, search_query)
#         ).order_by('-rank')
#         return posts

def home(request):
    context = {
        'posts':Post.objects.all().order_by('-likes')
    }
    return render(request, 'douban/home.html', context)

class SearchResultsView(ListView):
    model = Post
    template_name = 'douban/home.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        # 初始化查询集
        posts = Post.objects.all()
        # 从 url 中提取查询参数
        request = self.request
        query = self.request.GET.get('q', None)

        if query:
            if query.startswith('[') and query.endswith(']'):
                tag = query[1:-1]
                if tag and tag != 'None':
                    if self.request.user.is_authenticated:
                        posts = posts.filter(tags__name__in=[tag]).order_by('-likes').order_by('-favorites')
                    else:
                        posts = posts.filter(tags__name__in=[tag]).order_by('-date_posted')

            else:
                query = query.split(',')
                for word in query:
                    posts = posts.filter(
                        Q(title__icontains=word) |
                        Q(content__icontains=word)
                    )
                    if posts:
                        if self.request.user.is_authenticated:
                            res = posts.order_by('-likes').order_by('-favorites')
                            return res
                        else:
                            res = posts.order_by('-date_posted')
                            return res
        else:
            query = ''
        return posts

class PostListView(ListView):
    # <app>/<model>_<viewtype>.html
    model = Post
    template_name = 'douban/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

class UserPostListView(ListView):
    model = Post
    template_name = 'douban/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    mode = Post

    def get_queryset(self):
        return Post.objects.order_by('-date_posted')
        
    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        is_liked = False
        _id = self.object.id
        post = Post.objects.filter(id=_id).get()
        user_id = self.request.user.id
        if post.likes.filter(id=user_id).exists():
            is_liked = True
        context['is_liked'] = is_liked
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content','tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class TagUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

@login_required
def like_post(request):
    # _id = request.POST.get('post_id')
    _id = request.POST.get('id')
    post = get_object_or_404(Post, id=_id)
    is_liked = False
    user_id = request.user.id 
    if post.likes.filter(id=user_id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    context = {
        'post':post,
    }
    # if request.is_ajax():
    #     html = render_to_string('douban/like_section.html', context, request=request)
    return HttpResponseRedirect(request.path_info)

@login_required
def favorite_post(request):
    # _id = request.POST.get('post_id')
    _id = request.POST.get('id')
    post = get_object_or_404(Post, id=_id)
    user_id = request.user.id 
    is_favorited = False
    if post.favorites.filter(id=user_id).exists():
        post.favorites.remove(request.user)
        is_favorited = False
    else:
        post.favorites.add(request.user)
        is_favorited = True
    context = {
        'is_favorited':is_favorited,
    }
    if request.is_ajax():
        html = render_to_string('douban/favorite_section.html', context, request=request)
        return JsonResponse({'form':html})
