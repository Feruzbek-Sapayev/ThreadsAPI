from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Post, Media
from .serializers import PostSerializer, MediaSerializer


class UserPostsListView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        username = self.kwargs.get('username')  # yoki user_id bo'lishi mumkin
        return Post.objects.filter(user__username=username).order_by('-created_at')


# 📌 Barcha postlarni ko‘rish va yangi post yaratish
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# 📌 Faqat bitta postni ko‘rish
class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


# 📌 Media fayllarni yuklash (bir nechta rasm/video)
class MediaUploadView(generics.CreateAPIView):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        post_id = request.data.get('post')
        files = request.FILES.getlist('file')

        if not post_id or not files:
            return Response({'error': 'post and file(s) are required.'}, status=status.HTTP_400_BAD_REQUEST)

        media_objs = []
        for file in files:
            media = Media.objects.create(post_id=post_id, file=file)
            media_objs.append(media)

        return Response(MediaSerializer(media_objs, many=True).data, status=status.HTTP_201_CREATED)
