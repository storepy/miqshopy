from miqshop.utils import price_to_dict
from rest_framework import serializers


from miqshop.serializers import BaseProductListSerializer, BaseProductSizeSerializer, Product
from .models import Cart, OrderItem, Customer


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        read_only_fields = ('slug', 'product', 'price', 'subtotal')
        fields = ('size', 'quantity', *read_only_fields)

    product = BaseProductListSerializer()
    size = BaseProductSizeSerializer(read_only=True)
    price = serializers.DecimalField(
        source='get_price', decimal_places=2, max_digits=10, min_value=0)
    subtotal = serializers.DecimalField(
        source='get_subtotal', decimal_places=2, max_digits=10, min_value=0)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        read_only_fields = ('slug',)
        fields = ('name', 'phone', 'email', *read_only_fields)


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        read_only_fields = (
            'slug', 'customer', 'products',
            'items', 'items_count', 'subtotal'
        )
        fields = ('notes', 'dt_delivery', *read_only_fields)

    customer = CustomerSerializer(read_only=True)
    products = serializers.SlugRelatedField(
        slug_field="meta_slug", queryset=Product.objects.published(), many=True, required=False)
    items = OrderItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    # subtotal = serializers.DecimalField(
    #     source='get_subtotal', decimal_places=2, max_digits=10, min_value=0)

    def get_subtotal(self, instance):
        return price_to_dict(instance.get_subtotal())

    # def get_sale_price(self, instance):
        # return price_to_dict(instance.sale_price)
