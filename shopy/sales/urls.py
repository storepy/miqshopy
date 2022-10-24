from django.conf import settings
from django.urls import path, include

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns


from . import viewsets, views


app_name = 'sales'

router = routers.DefaultRouter()


router.register(r'carts', viewsets.CartViewset)
router.register(r'orders', viewsets.OrderViewset)
router.register(r'customers', viewsets.CustomerViewset)


generic_patterns = format_suffix_patterns(
    [
        # path(f'/{app_name}/cart/<str:slug>/', viewsets.CartViewset.as_view({'get': 'list'})),
    ]
)

urlpatterns = [
    # path('api/', include(router.urls)),
    path(f'{settings.API_PATH}/', include(router.urls)),

    path('staff/sales/orders/<slug:slug>/', views.StaffOrderDetailView.as_view(), name='stafforderdetail'),
    path('staff/sales/orders/', views.StaffOrderListView.as_view(), name='stafforderlist'),

    path('staff/sales/carts/<slug:slug>/', views.StaffCartUpdateView.as_view(), name='staffcartdetail'),
    path('staff/sales/carts/<slug:slug>/items/', views.StaffCartUpdateItemsView.as_view(), name='staffcartupdateitems'),

    path('staff/sales/', views.StaffSalesIndexView.as_view(), name='staffindex'),

    # path('/', include(generic_patterns)),
]
