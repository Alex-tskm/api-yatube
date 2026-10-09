from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    ObtainAuthTokenCustom,
    PostViewSet,
    GroupViewSet,
    CommentViewSet,
)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'groups', GroupViewSet, basename='group')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Подключаем класс через .as_view()
    path(
        'api/v1/api-token-auth/',
        ObtainAuthTokenCustom.as_view(),
        name='obtain_auth_token',
    ),
    path('api/v1/', include(router.urls)),
]

# Вложенные пути для комментариев
urlpatterns += [
    path(
        'api/v1/posts/<int:post_id>/comments/',
        CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='comment-list-create',
    ),
    path(
        'api/v1/posts/<int:post_id>/comments/<int:pk>/',
        CommentViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='comment-detail',
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
