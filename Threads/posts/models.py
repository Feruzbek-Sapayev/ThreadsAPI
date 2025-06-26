from django.db import models
import shortuuid
import os
from accounts.models import User


def generate_shortuuid():
    return shortuuid.uuid()[:11]


def random_file_path(instance, filename):
    ext = filename.split('.')[-1]
    random_name = generate_shortuuid()
    username = instance.post.author.username  # Bu yerda instance — PostMedia obyektidir
    return f'uploads/users/{username}/posts/{random_name}.{ext}'

class Post(models.Model):
    uid = models.CharField(default=generate_shortuuid, max_length=11, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post {self.uid}"

class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_media')
    media = models.FileField(upload_to=random_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def is_image(self):
        return self.media.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))

    def is_video(self):
        return self.media.name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))

    def __str__(self):
        return f"Media for Post {self.post.uid}"
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.uid}"
    

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']  # Har bir user faqat 1 marta like qilsin

    def __str__(self):
        return f"{self.user.username} liked {self.post.uid}"


class View(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)  # Agar user anonim bo‘lsa
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user', 'session_id')

    def __str__(self):
        return f"{self.user or self.session_id} viewed {self.post.uid}"

