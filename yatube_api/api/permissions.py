from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение на редактирование объекта только его владельцу.
    Владелец определяется по полю author (для Post, Comment).
    """

    def has_object_permission(self, request, view, obj):
        # Разрешены безопасные методы (GET, HEAD, OPTIONS) любому
        if request.method in permissions.SAFE_METHODS:
            return True

        # Запись (PUT, PATCH, DELETE) разрешена только владельцу
        return obj.author == request.user


class IsOwnerOrReadOnlyForWrite(permissions.BasePermission):
    """
    Разрешает чтение (GET) любому.
    Для записи (POST/PUT/PATCH/DELETE) — только автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) любому
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для записи — только если автор совпадает с пользователем
        return obj.author == request.user