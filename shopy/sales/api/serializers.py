
from miq.core.serializers import get_img_serializer_class

from ...store.serializers import get_product_serializer_class

from ..serializers import get_cart_serializer_class

__all__ = (
    'APIImageSerializer', 'APICartSerializer',
    'APIProductSerializer', 'APIProductListSerializer',
)

APIImageSerializer = get_img_serializer_class(
    extra_ro_fields=(
        'caption', 'alt_text',
        'height', 'height_mobile', 'height_thumb', 'height_thumb_sq',
        'width', 'width_mobile', 'width_thumb', 'width_thumb_sq',
    )
)

APIProductListSerializer = get_product_serializer_class(
    img_serializer=APIImageSerializer,
    extra_read_only_fields=(
        'url', 'meta_slug', 'name', 'name_truncated',
        'retail_price', 'retail_price_data', 'sale_price', 'sale_price_data',
        'cover_data', 'is_on_sale', 'is_oos', 'is_pre_sale'
    )
)
APIProductSerializer = get_product_serializer_class(
    img_serializer=APIImageSerializer,
    extra_read_only_fields=(
        'meta_slug', 'name', 'name_truncated', 'description',
        'price', 'retail_price', 'retail_price_data', 'sale_price', 'sale_price_data',
        'is_on_sale', 'is_oos', 'is_pre_sale', 'is_pre_sale_text', 'is_pre_sale_dt',
        'cover_data', 'images_data',
        'sizes', 'url', 'has_attributes', 'attributes',
    )
)

APICartSerializer = get_cart_serializer_class(
    extra_read_only_fields=(
        'slug', 'customer', 'customer_name', 'items', 'products',
        'subtotal', 'total'
    )
)
