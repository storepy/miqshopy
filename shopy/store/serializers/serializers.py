from django.utils.text import slugify

from rest_framework import serializers

from miq.staff.serializers import ImageSerializer

from ..models import ProductAttribute, ProductImage, ProductSize


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        read_only_fields = ('slug',)
        fields = ('name', 'code', 'quantity', *read_only_fields)

    def validate_code(self, value):
        return slugify(value)


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        read_only_fields = ('slug',)
        fields = ('name', 'value', *read_only_fields)


class ProductImageSerializer(ImageSerializer):
    class Meta(ImageSerializer.Meta):
        model = ProductImage
