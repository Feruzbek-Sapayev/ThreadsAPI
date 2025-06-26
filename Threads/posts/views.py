from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post, PostMedia, Like, View, Comment
from .serializers import PostSerializer, PostMediaSerializer, CommentSerializer, LikeSerializer, ViewSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'uid'


class UserPostsListView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        username = self.kwargs.get('username')  # yoki user_id bo'lishi mumkin
        return Post.objects.filter(author__username=username).order_by('-created_at')


class LikeToggleView(generics.ListCreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_uid = self.kwargs.get('uid')
        post = get_object_or_404(Post, uid=post_uid)
        return Like.objects.filter(post=post)

    def create(self, request, *args, **kwargs):
        post_uid = self.kwargs.get('uid')
        post = get_object_or_404(Post, uid=post_uid)

        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({'message': 'Unliked'}, status=status.HTTP_200_OK)
        return Response({'message': 'Liked'}, status=status.HTTP_201_CREATED)


class ViewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ViewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        uid = self.kwargs.get('uid')
        return View.objects.filter(post__uid=uid)

    def create(self, request, *args, **kwargs):
        uid = self.kwargs.get('uid')
        try:
            post = Post.objects.get(uid=uid)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=404)

        user = request.user if request.user.is_authenticated else None

        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        view_exists = View.objects.filter(
            post=post,
            user=user if user else None,
            session_id=session_id
        ).exists()

        if not view_exists:
            View.objects.create(
                post=post,
                user=user,
                session_id=session_id
            )

        return Response({'message': 'View registered'}, status=201)


class CommentCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_uid = self.kwargs.get('uid')
        return Comment.objects.filter(post__uid=post_uid)

    def perform_create(self, serializer):
        post_uid = self.kwargs.get('uid')
        post = Post.objects.get(uid=post_uid)
        serializer.save(author=self.request.user, post=post)


