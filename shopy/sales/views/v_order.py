
from ...store.utils import price_to_dict
from django.db import models

from miq.staff.views.generic import DetailView, ListView
from miq.core.serializers import serialize_context_pagination

from ..models import Order, OrderItem
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

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET

        if (cat := params.get('cat')):
            qs = qs.prefetch_related('products__category')\
                .filter(products__category__slug__in=[cat.lower()]).distinct()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = context['object_list']

        data = get_sales_view_base_context_data(self.request)
        data['total'] = {
            'amount': price_to_dict(self.object_list.total() or 0),
            'count': self.object_list.count(),
        }
        data['orders'] = OrderListSerializer(qs, many=True).data

        data['pagination'] = serialize_context_pagination(self.request, context)

        items = OrderItem.objects.filter(order__in=self.get_queryset())

        # top categories in items
        cats = items.values('product__category__name',)\
            .annotate(total=models.Count('product__category__name')).order_by('-total')\
            .values('product__category__slug', 'product__category__name', 'total')[:10]

        data['top_cats'] = list(cats)

        self.update_sharedData(context, data)

        return context
