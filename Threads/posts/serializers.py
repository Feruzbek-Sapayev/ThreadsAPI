from rest_framework import serializers
from .models import Post, Media
from accounts.serializers import UserSerializer

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'uploaded_at']

class PostSerializer(serializers.ModelSerializer):
    media_files = MediaSerializer(many=True, read_only=True)
    author = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'media_files']


