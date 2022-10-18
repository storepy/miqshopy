from django.conf import settings
from django.urls import path, re_path, include

from rest_framework import routers

from . import viewsets
from . import views

app_name = 'store'

staff_router = routers.DefaultRouter()
staff_router.register(r'products', viewsets.ProductViewset)
staff_router.register(r'categories', viewsets.CategoryViewset)
staff_router.register(r'supplierorders', viewsets.SupplierOrderViewset)
staff_router.register(r'shopy-settings', viewsets.ShopSettingViewset)
staff_router.register(r'shopy-analytics', viewsets.ShopAnalyticsViewset)
staff_router.register(r'shopy-insights', viewsets.StoreInsightsViewset)


urlpatterns = [
    path(f'{settings.API_PATH}/', include(staff_router.urls)),

    # path('trackr/', views.TrackrListView.as_view(), name="track"),
    path(f'staff/{app_name}/products/<slug:slug>/',
         views.StaffProductView.as_view(), name='product'),

    # Catch-all
    re_path(r'staff/store/', views.ShopStaffIndexView.as_view(), name='index'),
]
