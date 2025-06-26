from rest_framework import serializers
from .models import Post, PostMedia
from accounts.serializers import UserSerializer


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['media', 'uploaded_at']


class PostSerializer(serializers.ModelSerializer):
    media = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    author = UserSerializer()

    class Meta:
        model = Post
        fields = ['uid', 'author', 'content', 'created_at', 'media', 'images', 'videos']

    def create(self, validated_data):
        media_files = validated_data.pop('media', [])
        post = Post.objects.create(**validated_data)

        for media in media_files:
            PostMedia.objects.create(post=post, media=media)

        return post
    
    def get_videos(self, obj):
        videos = [media for media in obj.post_media.all() if media.is_video()]
        return PostMediaSerializer(videos, many=True, context=self.context).data
    
    def get_images(self, obj):
        images = [media for media in obj.post_media.all() if media.is_image()]
        return PostMediaSerializer(images, many=True, context=self.context).data

