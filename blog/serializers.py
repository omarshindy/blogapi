from rest_framework import serializers
from .models import Post, Category, Tag, Comment, Profile
from core.serializers import DynamicFieldsModelSerializer, ProfileSerializer

class CategorySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class TagSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class PostSerializer(DynamicFieldsModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'categories', 'tags', 'created_at', 'updated_at']

class CommentSerializer(DynamicFieldsModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']
