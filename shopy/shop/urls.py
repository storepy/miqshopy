from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views
from ..store.viewsets.suppliers import add_order_feed

app_name = 'shop'


urlpatterns = [
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
