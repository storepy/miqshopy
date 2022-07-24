from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import api
from . import views
from ..store.viewsets.suppliers import add_order_feed

app_name = 'shop'


urlpatterns = [
    path('api/order/customer/', api.post_customer, name='api_customer'),
    # path('api/order/cart/', api.patch_cart, name='api_cart'),
    path('api/order/cart/<slug:product_slug>/', api.post_orderitem, name='api_cart_post_product'),
    path('api/order/item/<slug:item_slug>/', api.patch_orderitem, name='api_cart_patch_item'),
]

urlpatterns += [
    path(
        f'{app_name}/feed/<slug:order_slug>/',
        csrf_exempt(add_order_feed), name='product_feed'),
    path(
        f'{app_name}/fb-products/',
        views.ProductsFbDataFeed.as_view(), name='fb_products'),

    path(
        f'{app_name}/<slug:category_meta_slug>/',
        views.CategoryView.as_view(), name='category'),

    path(
        f'{app_name}/<slug:category_meta_slug>/<slug:meta_slug>/',
        views.ProductView.as_view(), name='product'),

    path(f'{app_name}/', views.ProductsView.as_view(), name='products'),
]
