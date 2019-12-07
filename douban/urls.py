from django.urls import path
from . import views
from .views import (
    PostListView, 
    PostDetailView, 
    PostCreateView, 
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    SearchResultsView,
    TagUpdateView
)

urlpatterns = [
    path('', SearchResultsView.as_view(), name='douban-home'),
    path('search/', SearchResultsView.as_view(), name='search-result'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/create/', PostCreateView.as_view(), name='post-create'),    
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/update/tag/', TagUpdateView.as_view(), name='tag-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/like/', views.like_post, name='like-post'),
    path('post/favorite/', views.favorite_post, name='favorite-post'),

]