

# from django.db.models.functions import Cast
# from django.db.models import Count, CharField
# from pprint import pprint
from django.contrib.sites.shortcuts import get_current_site
# from django.http import JsonResponse

# from rest_framework import serializers
# from rest_framework.response import Response
# from rest_framework.decorators import api_view

from miq.staff.views.generic import DetailView
from miq.staff.views import IndexView

from ...store.serializers import ShopSettingSerializer, ProductListSerializer
from ...store.models import Product, ShopSetting

from ..models import Cart
from ..serializers import get_cart_serializer_class


def get_base_context_data(request):
    data = {}

    if (setting := ShopSetting.objects.filter(site=get_current_site(request))) and setting.exists():
        data['shopy_settings'] = ShopSettingSerializer(setting.first()).data
    return data


class StaffSalesIndexView(IndexView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = get_base_context_data(self.request)

        self.update_sharedData(context, data)

        return context


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

        data = get_base_context_data(self.request)
        data['cart'] = CartSerializer(self.object).data

        self.update_sharedData(context, data)

        return context


class StaffCartUpdateItemsView(StaffCartUpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = {
            'products': ProductListSerializer(Product.objects.order_by('-created').to_cart()[:16], many=True).data
        }

        self.update_sharedData(context, data)

        return context
