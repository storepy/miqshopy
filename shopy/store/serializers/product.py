from rest_framework import serializers

from ..utils import price_to_dict
from ..models import Product, ProductImage, Category


from .category import CategorySerializer
from .serializers import ProductAttributeSerializer, ProductImageSerializer, ProductSizeSerializer
from .suppliers import SupplierItemSerializer


class ProductSerializerMixin:

    def get_price(self, obj: Product):
        return price_to_dict(obj.get_price())

    def get_retail_price_data(self, obj: Product):
        return price_to_dict(obj.retail_price)

    def get_sale_price_data(self, obj: Product):
        return price_to_dict(obj.sale_price)


def get_product_serializer_class(*, request=None, extra_fields=(), extra_read_only_fields=(), img_serializer=None, whatsapp_number=None):
    """
    Returns a ProductSerializer class with extra fields and read_only_fields.
    extra_field choices include all fields from the Product model field names.
    extra_read_only_fields choices include all fields from the Product model field names
    and the following additional fields:
    name_truncated, cover_data, category_data
    retail_price_data, sale_price_data
    size_count, sizes, stage_choices
    attributes, images_data, supplier_item, add_to_cart_count
    """

    read_only_fields = (*extra_read_only_fields,)
    fields = (*read_only_fields, *extra_fields, )

    props = {
        'Meta': type('Meta', (), {
            'model': Product,
            'fields': fields,
            'read_only_fields': read_only_fields,
        })
    }

    ImgSerializer = img_serializer or ProductImageSerializer

    # FIELD

    if 'cover' in fields:
        props['cover'] = serializers.SlugRelatedField(
            slug_field="slug", queryset=ProductImage.objects.all(), required=False)
    if 'category' in extra_fields:
        props['category'] = serializers.SlugRelatedField(
            slug_field="slug", queryset=Category.objects.all(), required=False)

    if 'images' in extra_fields:
        props['images'] = serializers.SlugRelatedField(
            slug_field="slug", queryset=ProductImage.objects.all(),
            many=True, required=False
        )

    # READ ONLY FIELDS

    if 'shop_link' in read_only_fields:
        props['shop_link'] = serializers.SerializerMethodField(read_only=True)

        def get_shop_link(self, obj: Product):
            if not whatsapp_number:
                return None
            return obj.get_whatsapp_link(self.get_request(), whatsapp_number)

        props['get_shop_link'] = get_shop_link

    if 'url' in read_only_fields:
        props['url'] = serializers.CharField(source='path', read_only=True)

    if 'name_truncated' in extra_read_only_fields:
        props['name_truncated'] = serializers.ReadOnlyField()

    if 'cover_data' in extra_read_only_fields:
        props['cover_data'] = ImgSerializer(source='cover', read_only=True)

    if 'category_data' in extra_read_only_fields:
        props['category_data'] = CategorySerializer(source='category', read_only=True)

    if "price" in extra_read_only_fields:
        props['price'] = serializers.SerializerMethodField(read_only=True)

    if 'retail_price_data' in extra_read_only_fields:
        props['retail_price_data'] = serializers.SerializerMethodField(read_only=True)

    if 'sale_price_data' in extra_read_only_fields:
        props['sale_price_data'] = serializers.SerializerMethodField(read_only=True)

    if 'size_count' in extra_read_only_fields:
        props['size_count'] = serializers.IntegerField(source='sizes.count', read_only=True)
    if 'sizes' in extra_read_only_fields:
        props['sizes'] = ProductSizeSerializer(many=True, read_only=True)

    if 'stage_choices' in extra_read_only_fields:
        props['stage_choices'] = serializers.JSONField(read_only=True)

    if 'has_attributes' in extra_read_only_fields:
        props['has_attributes'] = serializers.BooleanField(source='attributes.count', read_only=True)

    if 'attributes' in extra_read_only_fields:
        props['attributes'] = ProductAttributeSerializer(many=True, read_only=True)

    if 'images_data' in extra_read_only_fields:
        props['images_data'] = ImgSerializer(source='images', many=True, read_only=True)

    if 'supplier_item' in extra_read_only_fields:
        props['supplier_item'] = SupplierItemSerializer(read_only=True)

    if 'add_to_cart_count' in extra_read_only_fields:
        props['add_to_cart_count'] = serializers.IntegerField(
            source='order_items.count', read_only=True)

    return type('ProductSerializer', (ProductSerializerMixin, serializers.ModelSerializer), props)


ProductListSerializer = get_product_serializer_class(
    extra_read_only_fields=(
        'slug', 'name_truncated', 'category_data', 'cover_data', 'sizes',
        'retail_price_data', 'sale_price_data', 'size_count', 'supplier_item',
        'stage', 'dt_published', 'is_published', 'add_to_cart_count', 'url',
    ),
    extra_fields=(
        'meta_slug', 'name', 'description', 'category', 'cover',
        'retail_price', 'is_on_sale', 'sale_price',
        'is_pre_sale', 'is_pre_sale_text', 'is_oos',
        'position', 'is_pinned', 'is_explicit'
    )
)

# TODO: add tests


ProductSerializer = get_product_serializer_class(
    extra_read_only_fields=(
        'slug', 'name_truncated', 'category_data', 'cover_data', 'sizes',
        'retail_price_data', 'sale_price_data',
        # 'size_count',
        'supplier_item',
        'stage', 'dt_published', 'is_published',
        'images_data', 'attributes', 'stage_choices', 'created', 'updated',
    ),
    extra_fields=(
        'name', 'description', 'category', 'cover',
        'retail_price', 'is_on_sale', 'sale_price',
        'is_explicit', 'is_oos', 'is_pinned', 'is_published',
        'is_pre_sale', 'is_pre_sale_text', 'is_pre_sale_dt',
        'images', 'position', 'supplier_item_id', 'color_group_pk', 'stage',
        'meta_title', 'meta_slug', 'meta_description'
    )
)
