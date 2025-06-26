from django.urls import path, re_path
from .views import PostListView, PostDetailView, UserPostsListView, PostCreateView


urlpatterns = [
    re_path(r'^add/?$', PostCreateView.as_view(), name='post-create'),
    re_path(r'^(?P<uid>[a-zA-Z0-9]+)/?$', PostDetailView.as_view(), name='post-detail')
    # path('', PostListView.as_view(), name='post-list'),
    # path('<str:username>/', UserPostsListView.as_view(), name='user-posts'),
]
