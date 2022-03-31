
from rest_framework.serializers import ModelSerializer, SlugRelatedField, JSONField, DecimalField

from ..models import Product, SupplierOrder, SupplierItem


__all__ = ('SupplierItemSerializer', 'SupplierOrderSerializer')


class SupplierItemSerializer(ModelSerializer):
    class Meta:
        model = SupplierItem
        read_only_fields = ('slug', 'created', 'updated',)
        fields = ('item_sn', 'category', 'url', 'cost', *read_only_fields)


class SupplierOrderSerializer(ModelSerializer):
    class Meta:
        model = SupplierOrder
        read_only_fields = (
            'slug', 'products', 'items', 'items_cost', 'items_revenue', 'avg_cost',
        )
        fields = (
            #  'items_stage',
            'name', 'order_id', 'supplier',
            'currency', 'is_paid', 'is_paid_dt', 'is_fulfilled_dt', 'total_cost',
            *read_only_fields
        )

    avg_cost = DecimalField(source='get_avg_cost', max_digits=10, decimal_places=2, read_only=True)
    items_cost = JSONField(source='get_items_cost', read_only=True)
    items_revenue = JSONField(source='get_items_revenue', read_only=True)
    products = SlugRelatedField(
        slug_field="slug", queryset=Product.objects.all(),
        many=True, required=False
    )


# SupplierOrder.objects.get(slug='68148363-f9df-4c9f-bc2a-3c2320db46ca').delete()
