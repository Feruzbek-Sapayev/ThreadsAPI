from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post, PostMedia, Like, View, Comment, UserInteraction
from .serializers import PostSerializer, PostMediaSerializer, CommentSerializer, LikeSerializer, ViewSerializer
from rest_framework.decorators import api_view, permission_classes, APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import get_object_or_404


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # bu yerda request uzatilyapti
        return context


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'uid'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # bu yerda request uzatilyapti
        return context


class UserPostsListView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        username = self.kwargs.get('username')  # yoki user_id bo'lishi mumkin
        return Post.objects.filter(author__username=username).order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # bu yerda request uzatilyapti
        return context


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
        UserInteraction.objects.create(
            user=request.user,
            post=post,
            action='like'
        )
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


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_uid = self.kwargs.get('uid')
        return Comment.objects.filter(post__uid=post_uid)

    def perform_create(self, serializer):
        post_uid = self.kwargs.get('uid')
        post = Post.objects.get(uid=post_uid)
        UserInteraction.objects.create(
            user=self.request.user,
            post=post,
            action='comment'
        )
        serializer.save(author=self.request.user, post=post)


class RecommendedPostsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = request.user
        posts = Post.objects.all()

        # Agar foydalanuvchi autentifikatsiya qilingan bo'lsa, tavsiya algoritmini qo'llaymiz
        if user.is_authenticated:
            # Foydalanuvchi yoqtirgan postlar matni va hashtaglarini olish
            liked_posts = UserInteraction.objects.filter(user=user, action='like').values_list('post__content', flat=True)
            liked_tags = UserInteraction.objects.filter(user=user, action='like').values_list('post__tags__name', flat=True)
            liked_texts = []
            for content in liked_posts:
                content = content if content else ''
                tags = ' '.join([tag for tag in liked_tags if tag])  # Hashtaglarni birlashtirish
                combined_text = f"{content} {tags}".strip()
                if combined_text:
                    liked_texts.append(combined_text)

            if liked_texts:
                # Post matnlari va hashtaglarini olish
                post_texts = []
                for post in posts:
                    content = post.content if post.content else ''
                    tags = ' '.join([tag.name for tag in post.tags.all()])
                    combined_text = f"{content} {tags}".strip()
                    if combined_text:
                        post_texts.append(combined_text)

                if not post_texts:
                    # Agar matnlar bo'lmasa, so'nggi postlarni qaytarish
                    recommended_posts = posts.order_by('-created_at')[:20]
                else:
                    # TF-IDF vektorizatsiya
                    vectorizer = TfidfVectorizer()
                    tfidf_matrix = vectorizer.fit_transform(post_texts)
                    user_tfidf = vectorizer.transform([' '.join(liked_texts)])

                    # O'xshashlikni hisoblash
                    similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
                    # Indekslarni tartiblash va int ga aylantirish
                    recommended_indices = [int(i) for i in similarities.argsort()[-20:][::-1] if i < len(posts)]
                    # Tartiblangan postlarni olish
                    recommended_posts = [posts[i] for i in recommended_indices]
            else:
                # Agar yoqtirilgan postlar bo'lmasa, so'nggi postlarni qaytarish
                recommended_posts = posts.order_by('-created_at')[:20]
        else:
            # Autentifikatsiya qilinmagan foydalanuvchilar uchun so'nggi postlar
            recommended_posts = posts.order_by('-created_at')[:20]

        serializer = PostSerializer(recommended_posts, many=True, context={'request': request})
        return Response(serializer.data)