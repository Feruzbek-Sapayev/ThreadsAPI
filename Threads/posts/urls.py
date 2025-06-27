from django.urls import path, re_path
from .views import PostDetailView, UserPostsListView, PostCreateView, LikeToggleView, CommentCreateView, ViewListCreateAPIView, RecommendedPostsView


urlpatterns = [
    re_path(r'^recommended/?$', RecommendedPostsView.as_view(), name='post-list'),
    re_path(r'^add/?$', PostCreateView.as_view(), name='post-create'),
    re_path(r'^(?P<uid>[a-zA-Z0-9]+)/like/?$', LikeToggleView.as_view(), name='post-like'),
    re_path(r'^(?P<uid>[a-zA-Z0-9]+)/view/?$', ViewListCreateAPIView.as_view(), name='post-view'),
    re_path(r'^(?P<uid>[a-zA-Z0-9]+)/comments/?$', CommentCreateView.as_view(), name='post-comment'),
    re_path(r'^(?P<uid>[a-zA-Z0-9]+)/?$', PostDetailView.as_view(), name='post-detail'),
    # path('<str:username>/', UserPostsListView.as_view(), name='user-posts'),
]
