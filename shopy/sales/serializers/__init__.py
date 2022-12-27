
from rest_framework import serializers

from miq.core.serializers import get_img_serializer_class

from ...store.utils import price_to_dict
from ...store.models import Product, ProductSize
from ...store.serializers import ProductSizeSerializer, get_product_serializer_class

from ..models import Customer, Order, Cart, OrderItem


"""
CUSTOMER
"""


class CustomerSerializerMixin:
    def get_total_amount_spent(self, obj):
        # if not obj.total:
        #     return price_to_dict(0)
        return price_to_dict(obj.get_total_amount_spent())


class CustomerSerializer(CustomerSerializerMixin, serializers.ModelSerializer):
    class Meta():
        model = Customer
        read_only_fields = ('slug', 'name', 'user', 'total_amount_spent', 'created', 'updated')
        fields = ('first_name', 'last_name', 'phone', 'email', *read_only_fields)

    total_amount_spent = serializers.SerializerMethodField(read_only=True)


def get_customer_serializer_class(*, extra_fields=(), extra_read_only_fields=()):
    """
    Returns a CustomerSerializer class with the given extra fields and read only fields.
    read_only_fields = slug, name + extra_read_only_fields
    extra_read_only_fields = user, orders_count, created, updated
    extra_fields = first_name, last_name, phone, email
    fields = (*read_only_fields, *extra_fields)
    """
    read_only_fields = ('slug', 'name', * extra_read_only_fields)
    fields = (*read_only_fields, *extra_fields)

    props = {
        'Meta': type('Meta', (), {
            'model': Customer,
            'fields': fields,
            'read_only_fields': read_only_fields,
        }),
        # 'customer_name': serializers.CharField(source='customer.name', read_only=True),
        # 'total': serializers.SerializerMethodField(read_only=True),
    }

    if 'total_amount_spent' in read_only_fields:
        props['total_amount_spent']: serializers.SerializerMethodField(read_only=True)

    if 'orders_count' in read_only_fields:
        props['orders_count'] = serializers.IntegerField(read_only=True, source='orders.count')

    if 'spent' in read_only_fields:
        props['spent'] = serializers.ReadOnlyField(read_only=True,)

    # if 'items' in read_only_fields:
    #     props['items'] = OrderItemSerializer(read_only=True, many=True)

    return type('CustomerSerializer', (CustomerSerializerMixin, serializers.ModelSerializer,), props)


"""
ORDERITEM
"""


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta():
        model = OrderItem
        read_only_fields = ('slug', 'product', 'size_data')
        fields = ('quantity', 'size', *read_only_fields)

    # product = ProductSerializer(read_only=True,)
    ProductImageSerializer = get_img_serializer_class(
        extra_ro_fields=('caption',)
    )
    ProductSerializer = get_product_serializer_class(
        img_serializer=ProductImageSerializer,
        extra_read_only_fields=(
            # 'slug',
            'meta_slug', 'name', 'name_truncated', 'cover', 'cover_data',
            'price', 'retail_price', 'retail_price_data', 'sale_price', 'sale_price_data',
            'is_on_sale', 'is_oos',
        )
    )
    product = ProductSerializer(read_only=True,)

    size = serializers.SlugRelatedField(
        slug_field="slug", queryset=ProductSize.objects.all(),
        required=False)
    size_data = ProductSizeSerializer(read_only=True, source='size')


"""
CART
"""


class CartSerializerMixin:
    def get_subtotal(self, obj):
        return price_to_dict(obj.get_subtotal())

    def get_total(self, obj):
        if not obj.total:
            return None
        return price_to_dict(obj.total)


class CartSerializer(CartSerializerMixin, serializers.ModelSerializer):
    class Meta():
        model = Cart
        read_only_fields = (
            'slug', 'customer_data', 'is_placed', 'items', 'products',
            'subtotal', 'total', 'created', 'updated',)
        fields = ('customer', 'notes', 'dt_delivery', *read_only_fields)

    customer = serializers.SlugRelatedField(
        slug_field="slug", queryset=Customer.objects.all(), required=False)
    customer_data = CustomerSerializer(read_only=True, source='customer')
    items = OrderItemSerializer(read_only=True, many=True)
    products = serializers.SlugRelatedField(
        slug_field="slug", queryset=Product.objects.published(),
        many=True, required=False
    )

    subtotal = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)


def get_cart_serializer_class(*, request=None, extra_fields=(), extra_read_only_fields=()):
    read_only_fields = ('slug', 'customer_name', 'products', 'subtotal', 'total', *extra_read_only_fields)
    fields = (*read_only_fields, *extra_fields)

    props = {
        'Meta': type('Meta', (), {
            'model': Cart,
            'read_only_fields': read_only_fields,
            'fields': fields,
        }),
        'customer_name': serializers.CharField(source='customer.name', read_only=True),
        'subtotal': serializers.SerializerMethodField(read_only=True),
        'total': serializers.SerializerMethodField(read_only=True),
    }

    if 'customer' in fields or 'customer' in read_only_fields:
        props['customer'] = serializers.SlugRelatedField(
            slug_field="slug", queryset=Customer.objects.all(), required=False)
    if 'customer_data' in read_only_fields:
        props['customer_data'] = CustomerSerializer(read_only=True, source='customer')

    if 'products' in fields or 'products' in read_only_fields:
        props['products'] = serializers.SlugRelatedField(
            slug_field="meta_slug", queryset=Product.objects.published(), many=True, required=False)
    if 'items' in read_only_fields:
        props['items'] = OrderItemSerializer(read_only=True, many=True)

    return type('CartSerializer', (CartSerializerMixin, serializers.ModelSerializer), props)


"""
ORDER
"""


def get_order_serializer_class(*, request=None, extra_fields=(), extra_read_only_fields=()):
    read_only_fields = ('slug', 'customer_name', 'subtotal', 'total', *extra_read_only_fields)
    fields = (*read_only_fields, *extra_fields)

    props = {
        'Meta': type('Meta', (), {
            'model': Order,
            'read_only_fields': read_only_fields,
            'fields': fields,
        }),
        'customer_name': serializers.CharField(source='customer.name', read_only=True),
        'subtotal': serializers.SerializerMethodField(read_only=True),
        'total': serializers.SerializerMethodField(read_only=True),
    }

    if 'customer_data' in read_only_fields:
        props['customer_data'] = CustomerSerializer(read_only=True, source='customer')

    if 'items' in read_only_fields:
        props['items'] = OrderItemSerializer(read_only=True, many=True)

    return type('OrderSerializer', (CartSerializerMixin, serializers.ModelSerializer), props)


OrderSerializer = get_order_serializer_class(
    extra_fields=('is_delivered',),
    extra_read_only_fields=(
        'transaction_id', 'customer_data', 'items',
        'items_count', 'dt_delivered', 'created', 'updated')
)
