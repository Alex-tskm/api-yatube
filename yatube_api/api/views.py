from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import PostSerializer, GroupSerializer, CommentSerializer
from posts.models import Post, Group, Comment


# --- ViewSets для API ---

class PostViewSet(ModelViewSet):
    """
    Все запросы (включая GET) требуют авторизации (IsAuthenticated).
    Редактировать/удалять может только автор.
    """
    queryset = Post.objects.all().select_related('author', 'group')
    serializer_class = PostSerializer

    permission_classes: list[object] = [IsAuthenticated]
    authentication_classes: list[object] = [TokenAuthentication]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _check_author(self, instance: Post) -> None:
        if instance.author != self.request.user:
            raise PermissionError()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self._check_author(instance)
        except PermissionError:
            return Response(
                {'detail': 'Вы не можете редактировать чужой пост'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self._check_author(instance)
        except PermissionError:
            return Response(
                {'detail': 'Вы не можете редактировать чужой пост'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self._check_author(instance)
        except PermissionError:
            return Response(
                {'detail': 'Вы не можете удалять чужой пост'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class GroupViewSet(ReadOnlyModelViewSet):
    """API для групп: только чтение."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    authentication_classes: list[object] = [TokenAuthentication]
    permission_classes: list[object] = [IsAuthenticated]


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes: list[object] = [IsAuthenticated]
    authentication_classes: list[object] = [TokenAuthentication]

    def get_queryset(self) -> QuerySet[Comment]:
        # Сначала получаем пост, если его нет — будет 404, а не пустой список
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        # Возвращаем комментарии через related_name
        # (предполагается, что в Post есть related_name='comments')
        return post.comments.all().select_related('author', 'post')

    def perform_create(self, serializer):
        # Проверяем существование поста ДО сохранения комментария
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)

    def _check_author(self, instance: Comment) -> None:
        if instance.author != self.request.user:
            raise PermissionError()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self._check_author(instance)
        except PermissionError:
            return Response(
                {'detail': 'Вы не можете редактировать чужой комментарий'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self._check_author(instance)
        except PermissionError:
            return Response(
                {'detail': 'Вы не можете редактировать чужой комментарий'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self._check_author(instance)
        except PermissionError:
            return Response(
                {'detail': 'Вы не можете удалять чужой комментарий'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
