from django.core.exceptions import PermissionDenied

from rest_framework import viewsets, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend

from .models import Post, Category, Tag, Comment
from .serializers import PostSerializer, CategorySerializer, TagSerializer, CommentSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'content']
    filterset_fields = ['categories', 'tags']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user.profile:
            raise PermissionDenied('You do not have permission to edit this post.')
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user.profile:
            raise PermissionDenied('You do not have permission to delete this post.')
        super().perform_destroy(instance)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

    def perform_destroy(self, instance):
        if instance.author != self.request.user.profile:
            raise PermissionDenied('You do not have permission to delete this comment.')
        super().perform_destroy(instance)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
