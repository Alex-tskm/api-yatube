from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import PostViewSet, GroupViewSet, CommentViewSet

# Роутер для версии v1 — версионирование живёт внутри приложения
v1_router = DefaultRouter()
v1_router.register(r'posts', PostViewSet, basename='post')
v1_router.register(r'groups', GroupViewSet, basename='group')

# Вложенный ресурс: post_id будет в kwargs вьюсета
v1_router.register(
    r'posts/(?P<post_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    # Стандартный DRF эндпоинт для токена
    path('v1/api-token-auth/', obtain_auth_token, name='obtain_auth_token'),
    # Подключаем все зарегистрированные ресурсы
    path('v1/', include(v1_router.urls)),
]
