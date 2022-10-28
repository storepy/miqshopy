
from rest_framework.serializers import ModelSerializer, SlugRelatedField, JSONField, DecimalField, SerializerMethodField

from ..utils import price_to_dict
from ..models import Product, SupplierOrder, SupplierItem


__all__ = ('SupplierItemSerializer', 'SupplierOrderSerializer')


class SupplierItemSerializer(ModelSerializer):
    class Meta:
        model = SupplierItem
        read_only_fields = ('slug', 'cost_at_rate_data', 'cost_data', 'rate_data', 'created', 'updated')
        fields = ('item_sn', 'category', 'url', 'cost', *read_only_fields)


class SupplierOrderSerializer(ModelSerializer):
    class Meta:
        model = SupplierOrder
        read_only_fields = (
            'slug', 'is_paid', 'products', 'items', 'items_cost', 'items_revenue', 'avg_cost',
            'rate', 'is_paid_dt', 'is_fulfilled_dt', 'total_cost_data', 'total_cost_at_rate_data',
        )
        fields = (
            'name', 'order_id', 'supplier',
            'total_cost',
            'currency', *read_only_fields
        )

    total_cost_data = SerializerMethodField(read_only=True)
    total_cost_at_rate_data = SerializerMethodField(read_only=True)
    avg_cost = DecimalField(source='get_avg_cost', max_digits=10, decimal_places=2, read_only=True)
    items_cost = JSONField(source='get_items_cost', read_only=True)
    items_revenue = JSONField(source='get_items_revenue', read_only=True)
    products = SlugRelatedField(
        slug_field="slug", queryset=Product.objects.all(),
        many=True, required=False
    )

    def get_total_cost_at_rate_data(self, obj: SupplierOrder) -> dict:
        if obj.is_paid:
            return obj.total_cost_at_rate_data
        return price_to_dict(float(obj.get_items_cost().get('amount')) * obj.rate, obj.currency)

    def get_total_cost_data(self, inst: SupplierOrder) -> dict:
        if inst.is_paid:
            return price_to_dict(inst.total_cost, inst.currency)
        return inst.get_items_cost()
