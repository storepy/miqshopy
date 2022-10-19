
from django.db import models
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

from ...store.utils import price_to_dict
from ...store.serializers import ShopSettingSerializer, get_product_serializer_class, ProductListSerializer as ProductSerializer
from ...store.models import Product, ShopSetting

from ..models import Cart, Order, Customer, OrderItem
from ..serializers import get_cart_serializer_class


def get_base_context_data(request):
    data = {}

    if (setting := ShopSetting.objects.filter(site=get_current_site(request))) and setting.exists():
        data['shopy_settings'] = ShopSettingSerializer(setting.first()).data

    return data


ProductListSerializer = get_product_serializer_class(
    extra_read_only_fields=(
        'slug', 'name', 'name_truncated', 'cover_data',
        'retail_price_data', 'sale_price_data', 'url',
    ),
)


class StaffSalesIndexView(IndexView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = get_base_context_data(self.request)

        orders = Order.objects.all()
        carts = Cart.objects.abandonned()
        placed = Cart.objects.placed()

        customers = Customer.objects.filter(orders__is_paid=True)
        prospects = Customer.objects.filter(orders__is_paid=False)

        items = OrderItem.objects.all()

        top_cart = items.values('product__slug').annotate(
            total=models.Count('product__slug')).order_by('-total')[:10]
        top_selling = items.filter(order__is_paid=True).values('product__slug').annotate(
            total=models.Count('product__slug')).order_by('-total')[:10]

        data.update({
            'total': price_to_dict(orders.total()),
            'orders_count': orders.count(),
            'carts_count': carts.count(),
            'placed_count': placed.count(),

            'customers_count': customers.count(),
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

        qs = Product.objects.order_by('-created').to_cart()
        if(q := self.request.GET.get('q')) and q != '':
            qs = qs.search_by_query(q)

        data = {
            'products': ProductSerializer(qs[:16], many=True).data
        }

        self.update_sharedData(context, data)

        return context
