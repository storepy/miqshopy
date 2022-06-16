from rest_framework import serializers

from ..utils import price_to_dict
from ..models import Product, ProductImage, Category


from .category import CategorySerializer
from .serializers import ProductAttributeSerializer, ProductImageSerializer, ProductSizeSerializer
from .suppliers import SupplierItemSerializer


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        read_only_fields = (
            'slug', 'name_truncated', 'category_data', 'cover_data',
            'retail_price_data', 'sale_price_data', 'size_count', 'supplier_item',
            #
            'dt_published', 'is_published'

        )
        fields = (
            *read_only_fields,
            'name', 'description', 'category', 'cover',
            'retail_price', 'is_on_sale', 'sale_price',
            'is_pre_sale', 'is_pre_sale_text', 'is_oos',
            'position',
        )

    # region fields

    name_truncated = serializers.ReadOnlyField()
    cover = serializers.SlugRelatedField(
        slug_field="slug", queryset=ProductImage.objects.all(), required=False)
    cover_data = ProductImageSerializer(source='cover', read_only=True)

    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all(), required=False)
    category_data = CategorySerializer(source='category', read_only=True)

    supplier_item = SupplierItemSerializer(read_only=True)
    size_count = serializers.IntegerField(source='sizes.count', read_only=True)
    # add_to_cart_count = serializers.IntegerField(
    #     source='order_items.count', read_only=True)

    retail_price_data = serializers.SerializerMethodField(read_only=True)
    sale_price_data = serializers.SerializerMethodField(read_only=True)

    # endregion fields

    def get_retail_price_data(self, obj):
        return price_to_dict(obj.retail_price)

    def get_sale_price_data(self, obj):
        return price_to_dict(obj.sale_price)


class ProductSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        read_only_fields = (
            *ProductListSerializer.Meta.read_only_fields, 'sizes',
            'images_data', 'attributes', 'stage_choices', 'created', 'updated',
        )
        fields = (
            *read_only_fields,
            'name', 'description', 'category', 'cover',
            'retail_price', 'is_on_sale', 'sale_price',
            'is_pre_sale', 'is_pre_sale_text', 'is_pre_sale_dt', 'is_oos',
            'images', 'position', 'supplier_item_id',
            'color_group_pk', 'stage',
            'is_published', 'meta_title', 'meta_slug', 'meta_description'
        )

    stage_choices = serializers.JSONField(read_only=True)
    sizes = ProductSizeSerializer(many=True, read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    images = serializers.SlugRelatedField(
        slug_field="slug", queryset=ProductImage.objects.all(),
        many=True, required=False
    )
    images_data = ProductImageSerializer(source='images', many=True, read_only=True)
