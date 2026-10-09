from django.contrib.auth import authenticate
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .serializers import PostSerializer, GroupSerializer, CommentSerializer
from posts.models import Post, Group, Comment


# --- Эндпоинт для получения токена (APIView) ---
class ObtainAuthTokenCustom(APIView):
    # Явно указываем типы для списков классов
    authentication_classes: list[object] = []
    permission_classes: list[object] = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'detail': 'username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'detail': 'User account is inactive'},
                status=status.HTTP_403_FORBIDDEN
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


# --- ViewSets для API ---

class PostViewSet(ModelViewSet):
    """
    Все запросы (включая GET) требуют авторизации (IsAuthenticated).
    Редактировать/удалять может только автор.
    """
    queryset = Post.objects.all().select_related('author', 'group')
    serializer_class = PostSerializer

    # Аннотации для mypy
    permission_classes: list[object] = [IsAuthenticated]
    authentication_classes: list[object] = [TokenAuthentication]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'Вы не можете редактировать чужой пост'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'Вы не можете редактировать чужой пост'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'Вы не можете удалять чужой пост'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class GroupViewSet(ReadOnlyModelViewSet):
    """API для групп: только чтение."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    # Аннотации для mypy
    authentication_classes: list[object] = [TokenAuthentication]
    permission_classes: list[object] = [IsAuthenticated]


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    # Аннотации для mypy
    permission_classes: list[object] = [IsAuthenticated]
    authentication_classes: list[object] = [TokenAuthentication]

    # Тип возвращаемого значения для совместимости с mypy
    def get_queryset(self) -> QuerySet[Comment]:
        post_id = self.kwargs.get('post_id')
        return (
            Comment.objects
            .filter(post_id=post_id)
            .select_related('author', 'post')
        )

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        serializer.save(author=self.request.user, post_id=post_id)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'Вы не можете редактировать чужой комментарий'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'Вы не можете редактировать чужой комментарий'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'Вы не можете удалять чужой комментарий'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
