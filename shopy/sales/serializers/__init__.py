
from rest_framework import serializers

from shopy.store.models import Product, ProductSize
from shopy.store.serializers import ProductSerializer, ProductSizeSerializer

from ...store.utils import price_to_dict
from ..models import Customer, Order, Cart, OrderItem


"""
CUSTOMER
"""


class CustomerSerializer(serializers.ModelSerializer):
    class Meta():
        model = Customer
        read_only_fields = ('slug', 'user', 'created', 'updated')
        fields = (
            'first_name', 'last_name', 'phone', 'email',
            *read_only_fields
        )


"""
ORDERITEM
"""


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta():
        model = OrderItem
        read_only_fields = ('slug', 'product', 'size_data')
        fields = ('quantity', 'size', *read_only_fields)

    product = ProductSerializer(read_only=True,)
    size = serializers.SlugRelatedField(
        slug_field="slug", queryset=ProductSize.objects.all(),
        required=False)
    size_data = ProductSizeSerializer(read_only=True, source='size')


"""
CART
"""


class CartSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        read_only_fields = (
            'slug', 'customer_data', 'items', 'products',
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

    def get_subtotal(self, obj):
        return price_to_dict(obj.get_subtotal())

    def get_total(self, obj):
        return price_to_dict(obj.total)


"""
ORDER
"""


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        read_only_fields = (
            'slug', 'customer', 'customer_data', 'total',
            'is_delivered', 'dt_delivered', 'items', 'items_count', 'added_by',
            'created', 'updated')
        fields = (
            'products', 'notes', 'dt_delivery',
            *read_only_fields
        )
