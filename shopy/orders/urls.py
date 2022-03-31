from django.conf import settings
from django.urls import path, include

from rest_framework import routers


from . import viewsets


app_name = 'orders'

router = routers.DefaultRouter()

router.register(r'orders-carts', viewsets.CartViewset)
router.register(r'orders-orders', viewsets.OrderViewset)
router.register(r'orders-customers', viewsets.CustomerViewset)

# router = routers.DefaultRouter()
# router.register(r'carts', CartViewset)


urlpatterns = [
    # path('api/', include(router.urls)),
    path(f'{settings.API_PATH}/', include(router.urls)),

    # path('orders/cart/', views.CartDetailView.as_view(), name='cart'),
    # path('orders/<slug:slug>/', views.OrderCreateView.as_view(), name='order_create'),
]
