

from miq.staff.views.generic import DetailView

from ...store.serializers import ProductListSerializer
from ...store.models import Product

from ..models import Cart
from ..serializers import get_cart_serializer_class

from .utils import get_sales_view_base_context_data


CartSerializer = get_cart_serializer_class(
    extra_fields=('customer', 'notes', 'dt_delivery'),
    extra_read_only_fields=(
        'slug', 'customer_name', 'customer_data', 'is_placed',
        'items', 'products',
        'subtotal', 'total', 'created', 'updated')
)


class StaffCartUpdateView(DetailView):
    model = Cart
    template_name = 'store/base.django.html'
    slug_field = 'slug'
    # slug_url_kwarg = 'product_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = get_sales_view_base_context_data(self.request)
        data['cart_data'] = CartSerializer(self.object).data

        self.update_sharedData(context, data)

        return context


class StaffCartUpdateItemsView(StaffCartUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = Product.objects.order_by('-created').to_cart()
        if(q := self.request.GET.get('q')) and q != '':
            qs = qs.search_by_query(q)

        data = {
            'products': ProductListSerializer(qs[:16], many=True).data
        }

        self.update_sharedData(context, data)

        return context
