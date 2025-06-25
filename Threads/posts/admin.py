from django.contrib import admin
from .models import Post, Media

class MediaInline(admin.TabularInline):
    model = Media
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [MediaInline]
    list_display = ['id', 'content', 'content', 'created_at', 'updated_at']
