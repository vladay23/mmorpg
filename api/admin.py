from django.contrib import admin
from .models import (
    Guide,
    News,
    Event,
    Comment,
    Subscription,
    Favorite
)

@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('created_at',)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('published_at',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'organizer')
    search_fields = ('title', 'description', 'organizer__username')
    list_filter = ('date',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'created_at')
    search_fields = ('content', 'author__username')
    list_filter = ('created_at',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_user', 'created_at')
    search_fields = ('user__username', 'target_user__username')

@admin.register(Favorite)
class FavoriteGuideAdmin(admin.ModelAdmin):
    list_display = ('user', 'added_at')
    search_fields = ('user__username', 'guide__title')
