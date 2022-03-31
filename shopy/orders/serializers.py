from rest_framework import serializers


from .models import Order, Cart


"""
CUSTOMER
"""


class CustomerSerializer(serializers.ModelSerializer):
    class Meta():
        read_only_fields = (
            'user', 'created', 'updated')
        fields = read_only_fields


"""
CART
"""


class CartSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        read_only_fields = (
            'created', 'updated', 'added_by')
        fields = read_only_fields

    customer = CustomerSerializer(read_only=True)


"""
ORDER
"""


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        read_only_fields = (
            'slug', 'customer_data', 'is_paid', 'total',
            'is_delivered', 'dt_delivered', 'items', 'items_count',
            'created', 'updated')
        fields = (
            'customer', 'products',
            'notes', 'dt_delivery',
            *read_only_fields
        )
