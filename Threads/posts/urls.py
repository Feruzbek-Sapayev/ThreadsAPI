from django.urls import path
from .views import PostListCreateView, PostDetailView, MediaUploadView, UserPostsListView

urlpatterns = [
    path('posts', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>', PostDetailView.as_view(), name='post-detail'),
    path('media/upload', MediaUploadView.as_view(), name='media-upload'),
    path('<str:username>', UserPostsListView.as_view(), name='user-posts'),
]
