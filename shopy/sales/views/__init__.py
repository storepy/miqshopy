
from django.db import models

from miq.staff.views import IndexView

from ...store.utils import price_to_dict
from ...store.serializers import get_product_serializer_class
from ...store.models import Product, SupplierOrder

from ..models import Cart, Order, Customer, OrderItem
from ..serializers import get_customer_serializer_class
from .utils import get_sales_view_base_context_data
from .v_order import StaffOrderDetailView, StaffOrderListView
from .v_cart import StaffCartUpdateView, StaffCartUpdateItemsView
from .v_customer import StaffCustomerListView, StaffCustomerDetailView


__all__ = (
    'StaffIndexView',
    'StaffOrderListView', 'StaffOrderDetailView',
    'StaffCartUpdateView', 'StaffCartUpdateItemsView',
    'StaffCustomerListView', 'StaffCustomerDetailView',
)


ProductListSerializer = get_product_serializer_class(
    extra_read_only_fields=(
        'slug', 'name', 'name_truncated', 'cover_data',
        'retail_price_data', 'sale_price_data', 'url',
    ),
)


class StaffSalesIndexView(IndexView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = get_sales_view_base_context_data(self.request)

        orders = Order.objects.all()
        carts = Cart.objects.abandonned()
        placed = Cart.objects.placed()

        supplier_orders = SupplierOrder.objects.all()

        customers = Customer.objects.filter(orders__is_paid=True)
        prospects = Customer.objects.filter(orders__is_paid=False)

        items = OrderItem.objects.all()

        top_cart = items.filter(order__is_paid=False).values('product__slug').annotate(
            total=models.Count('product__slug')).order_by('-total')[:10]
        top_selling = items.filter(order__is_paid=True).values('product__slug').annotate(
            total=models.Count('product__slug')).order_by('-total')[:10]

        total_by_month = {
            f'{value[0]}': {'total': value[1], 'month': f'{value[0]}'} for value in orders.total_by_month().values_list('month', 'total')
        }
        for value in orders.count_by_month().values_list('month', 'count'):
            total_by_month[f'{value[0]}']['count'] = value[1]

        data.update({
            'total': price_to_dict(orders.total()),
            'supplier_total': price_to_dict(supplier_orders.total(), currency='USD'),
            'orders_count': orders.count(),
            'carts_count': carts.count(),
            'placed_count': placed.count(),
            'total_by_month': total_by_month,

            'customers_count': customers.count(),
            'top_customers': get_customer_serializer_class(extra_read_only_fields=('orders_count',)).many_init(customers.by_amount_spent().order_by('-spent', )[:10]).data,
            'prospects_count': prospects.count(),

            'top_cart': [
                ProductListSerializer(Product.objects.get(slug=p)).data for p in top_cart.values_list('product__slug', flat=True)
            ],
            'top_selling': [
                ProductListSerializer(Product.objects.get(slug=p)).data for p in top_selling.values_list('product__slug', flat=True)
            ],
        })

        self.update_sharedData(context, data)

        return context
