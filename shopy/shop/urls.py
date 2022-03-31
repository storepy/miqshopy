from django.urls import path

from . import views


app_name = 'shop'


urlpatterns = [
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
