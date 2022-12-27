
# from django.db import models

from miq.staff.views.generic import DetailView, ListView
from miq.core.serializers import serialize_context_pagination

from ..models import Customer
from ..serializers import CustomerSerializer, get_customer_serializer_class

from .utils import get_sales_view_base_context_data


class StaffCustomerDetailView(DetailView):
    model = Customer
    template_name = 'store/base.django.html'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Customer - Sales'

        data = get_sales_view_base_context_data(self.request)
        data['customer_data'] = CustomerSerializer(self.object).data

        self.update_sharedData(context, data)

        return context


CustomerListSerializer = get_customer_serializer_class(extra_read_only_fields=('orders_count', 'spent'))


class StaffCustomerListView(ListView):
    queryset = Customer.objects.all().by_amount_spent().order_by('-created')
    template_name = 'store/base.django.html'
    slug_field = 'slug'
    paginate_by: int = 16

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'Customers - Sales'

        data = get_sales_view_base_context_data(self.request)
        data['customers'] = CustomerListSerializer(context['object_list'], many=True).data
        data['pagination'] = serialize_context_pagination(self.request, context)

        self.update_sharedData(context, data)

        return context
