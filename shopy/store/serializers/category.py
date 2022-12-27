
from rest_framework import serializers

from miq.core.models import Image

from ..models import Category

from .serializers import ProductImageSerializer

__all__ = ('get_category_serializer_class', 'CategorySerializer')


def get_category_serializer_class(*, extra_fields=(), extra_read_only_fields=(), img_serializer=None, ** kwargs):
    read_only_fields = (*extra_read_only_fields,)
    fields = (*read_only_fields, *extra_fields)
    props = {
        'Meta': type('Meta', (), {
            'model': Category,
            'fields': fields,
            'read_only_fields': read_only_fields
        })
    }

    ImgSerializer = img_serializer or ProductImageSerializer

    if 'parent' in fields:
        props['parent'] = serializers.SlugRelatedField(
            slug_field="slug", queryset=Category.objects.all(), required=False, allow_null=True
        )

    if 'parent_name' in read_only_fields and 'parent' in fields:
        props['parent_name'] = serializers.CharField(source='parent.name', read_only=True)

    if 'cover' in fields:
        props['cover'] = serializers.SlugRelatedField(
            slug_field="slug", queryset=Image.objects.all(), required=False
        )

    if 'cover_data' in extra_read_only_fields:
        props['cover_data'] = ImgSerializer(source='cover', read_only=True)

    if 'products_count' in extra_read_only_fields:
        props['products_count'] = serializers.IntegerField(read_only=True)

    if 'published_count' in extra_read_only_fields:
        props['published_count'] = serializers.IntegerField(read_only=True)

    if 'draft_count' in extra_read_only_fields:
        props['draft_count'] = serializers.IntegerField(read_only=True)

    return type('CategorySerializer', (serializers.ModelSerializer,), props)


CategorySerializer = get_category_serializer_class(
    extra_read_only_fields=(
        'slug', 'parent_name', 'dt_published', 'cover_data', 'is_published',
        'products_count', 'published_count', 'draft_count',
        'created', 'updated'
    ),
    extra_fields=(
        'parent', 'name', 'description', 'cover', 'position',
        'meta_title', 'meta_slug', 'meta_description',
    )
)
