# from pprint import pprint
from rest_framework import serializers

from miq.core.models import Image
from miq.staff.serializers import ImageSerializer

from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        read_only_fields = (
            'slug', 'dt_published', 'cover_data',
            'products_count', 'published_count', 'draft_count',
            'created', 'updated'
        )
        fields = (
            'name', 'description', 'cover', 'position',
            'meta_title', 'meta_slug', 'meta_description', 'is_published',
            *read_only_fields
        )

    cover = serializers.SlugRelatedField(
        slug_field="slug", queryset=Image.objects.all(), required=False
    )
    cover_data = ImageSerializer(source='cover', read_only=True)
    products_count = serializers.IntegerField(read_only=True)
    published_count = serializers.IntegerField(read_only=True)
    draft_count = serializers.IntegerField(read_only=True)
