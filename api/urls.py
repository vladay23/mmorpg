from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views


from .views import TestModelListCreateAPIView, NewsDetailAPIView, NewsListCreateAPIView, GuideListCreateAPIView, GuideDetailAPIView, EventListCreateAPIView, EventDetailAPIView, RegisterAPIView, UserDetailAPIView, PasswordChangeAPIView, LoginAPIView

urlpatterns = [
    # Гайды
    # API
    path('guides/', GuideListCreateAPIView.as_view(), name='api-guides-list'),
    path('guides/<int:pk>/', GuideDetailAPIView.as_view(), name='api-guide-detail'),

    # Веб-страницы (если нужны)
    path('guides/', views.guide_list_view, name='guide-list'),  # Можно убрать, если всё через API
    path('guides/<int:pk>/', views.guide_detail, name='guide-detail'),
    
    path('guides/create/', views.create_guide, name='create_guide'),
    path('guides/<int:pk>/edit/', views.create_guide, name='edit_guide'),
    
    # Новости
    # API endpoints
    path('news/', NewsListCreateAPIView.as_view(), name='api-news-list'),
    path('news/<int:pk>/', NewsDetailAPIView.as_view(), name='api-news-detail'),

    # Веб-страницы
    path('news/', views.news_list_view, name='news-list'),
    path('news/<int:pk>/', views.news_detail, name='news-detail'),

    path('news/create/', views.create_news, name='create_news'),
    path('news/<int:pk>/edit/', views.edit_news, name='news-edit'),

    # Мероприятия
    # API endpoints
    path('events/', EventListCreateAPIView.as_view(), name='api-events'),
    path('events/<int:pk>/', EventDetailAPIView.as_view(), name='api-event-detail'),

    # Веб-страницы
    path('events/', views.event_list_view, name='event-list'),
    path('events/<int:pk>/', views.event_detail, name='event-detail'),

    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:pk>/edit/', views.event_edit, name='event-edit'),

    # Комментарии
    # API endpoints
    #path('api/comments/', views.CommentListCreateAPIView.as_view(), name='api-comments'),
    #path('api/comments/<int:pk>/', views.CommentDetailAPIView.as_view(), name='api-comment-detail'),

    # Веб-страницы
    #path('comments/', views.comment_list_view, name='comment-list'),
    #path('comments/<int:pk>/', views.comment_detail, name='comment-detail'),

    path('comments/', views.CommentAPIView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', views.CommentAPIView.as_view(), name='comment-detail'),

    # Подписки
    # API endpoints
    #path('api/subscriptions/', views.SubscriptionListCreateAPIView.as_view(), name='api-subscriptions'),
    #path('api/subscriptions/<int:pk>/', views.SubscriptionDetailAPIView.as_view(), name='api-subscription-detail'),

    # Веб-страницы
    #path('subscriptions/', views.subscription_list_view, name='subscription-list'),
    #path('subscriptions/<int:pk>/', views.subscription_detail, name='subscription-detail'),

    # Пути для API-ресурса "Избранное"
    #path('api/favorites/', views.FavoritesListCreateAPIView.as_view(), name='api-favorites'),
    path('favorites/<int:pk>/', views.FavoriteViewSet.as_view({'get': 'list', 'post': 'create'}), name='api-favorite'),

    # Веб-страницы для "Избранного"
    #path('favorites/', views.favorites_list_view, name='favorites-list'),
    path('favorites/user/<int:user_id>/', views.user_favorites, name='user_favorites'),
    path('favorites/remove/<int:pk>/', views.remove_favorite, name='remove_favorite'),

    # API
    path('profiles/<int:pk>/', UserDetailAPIView.as_view(), name='userprofile-detail'),
    path('register/', RegisterAPIView.as_view(), name='api-register'),

    #Страницы
    path('register/', views.register_view, name='register'),
    #path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('password-change/', PasswordChangeAPIView.as_view(), name='password-change'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('tests/', TestModelListCreateAPIView.as_view(), name='testmodel-list-create'),


]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)