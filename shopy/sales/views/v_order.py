
# from django.db import models

from miq.staff.views.generic import DetailView, ListView
from miq.core.serializers import serialize_context_pagination

from ..models import Order
from ..serializers import get_order_serializer_class, OrderSerializer

from .utils import get_sales_view_base_context_data


OrderListSerializer = get_order_serializer_class(extra_read_only_fields=('items_count', 'created'))


class StaffOrderDetailView(DetailView):
    model = Order
    template_name = 'store/base.django.html'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = get_sales_view_base_context_data(self.request)
        data['order_data'] = OrderSerializer(self.object).data

        self.update_sharedData(context, data)

        return context


class StaffOrderListView(ListView):
    model = Order
    template_name = 'store/base.django.html'
    slug_field = 'slug'
    paginate_by: int = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = get_sales_view_base_context_data(self.request)
        data['orders'] = OrderListSerializer(context['object_list'], many=True).data
        data['pagination'] = serialize_context_pagination(self.request, context)

        self.update_sharedData(context, data)

        return context
