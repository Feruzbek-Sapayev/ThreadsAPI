from rest_framework import serializers
from .models import Post, PostMedia, Comment, Like, View
from accounts.serializers import UserSerializer


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['media', 'uploaded_at']


class PostSerializer(serializers.ModelSerializer):
    media = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    views_count = serializers.IntegerField(source='views.count', read_only=True)

    class Meta:
        model = Post
        fields = ['uid', 'author', 'content', 'created_at', 'media', 'images', 'videos', 'comments_count', 'likes_count', 'views_count']

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


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()


    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']

    def get_user(self, obj):
        return obj.user.username if obj.user else None

    def get_post(self, obj):
        return obj.post.uid if obj.post else None


class ViewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()


    class Meta:
        model = View
        fields = ['user', 'post', 'session_id', 'viewed_at']

    def get_user(self, obj):
        return obj.user.username if obj.user else None

    def get_post(self, obj):
        return obj.post.uid if obj.post else None
