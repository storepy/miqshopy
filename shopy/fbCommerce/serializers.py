from django.db import models
from rest_framework import serializers

from ..models import Product


class ProductCondition(models.TextChoices):
    a = 'new'
    b = 'refurbished'
    c = 'used'


class ProductAvailability(models.TextChoices):
    IN = 'in stock'
    AV = 'available for order'
    OU = 'out of stock'
    DI = 'discontinued'

# https://developers.facebook.com/docs/marketing-api/catalog/reference#supported-fields


class FbProductSerializer(serializers.ModelSerializer):

    product_type = serializers.CharField(source='category__name', read_only=True)
    # link: url, image_link: 1024 x 1024/1200 x 628
    # additional_image_link: 20 max/https://www.fb.com/t_shirt_2.jpg,https://www.fb.com/t_shirt_3.jpg
    # color, item_group_id, sale_price, size, status(active,archived)

    class Meta:
        model: Product
        read_only_fields = (
            'id', 'title', 'description', 'product_type'
            'availability', 'condition', 'price', 'link', 'status'
        )
        fields = read_only_fields
