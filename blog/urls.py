from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import PostViewSet, CategoryViewSet, TagViewSet, CommentViewSet

app_name = 'blog'

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
