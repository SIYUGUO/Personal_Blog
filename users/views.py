from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from douban.models import Post
import operator

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'You are ready to login!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, 
                                   request.FILES, 
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:        
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form':u_form,
        'p_form':p_form
    }
    return render(request, 'users/profile.html', context)

@login_required
def dashboard(request):
    username = request.user
    posts = Post.objects.all()
    user_posts = Post.objects.filter(author=username)
    context = {
        'posts':posts,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def recommendation(request):
    username = request.user
    posts = Post.objects.all()

    original_user = User.objects.filter(username=username).first()
    user_set = User.objects.all()
    others = dict()
    for user in user_set:
        if user != original_user:
            others[user] = others.get(user, 0) + 1
            for post in posts:
                if post.likes.filter(username=user).exists() and post.likes.filter(username=original_user).exists():
                    others[user] += 1
                if post.favorites.filter(username=user).exists() and post.favorites.filter(username=original_user).exists():
                    others[user] += 2

    # sort my dict, get the first key-item, that is the most similar user
    others_list = []
    others_list = sorted(others.items(), key=operator.itemgetter(1), reverse=True)
    similar_user = others_list[0][0]

    r_user = User.objects.filter(username=similar_user).first()

    list_of_post_ids = []

    for post in posts:
        if post.favorites.filter(username=similar_user).exists():
            if not post.favorites.filter(username=original_user).exists():
                list_of_post_ids.append(post.id)

    queryset = Post.objects.filter(id__in=list_of_post_ids)

    context = {
        'posts':queryset,
    }
    return render(request, 'users/recommendation.html', context)
