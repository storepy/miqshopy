from django.urls import path, include
from shopy.shop import views

urlpatterns = [
    path('', include('shopy.store.urls', namespace='store')),
    path('', include('shopy.shop.urls', namespace='shop')),
    path('', include('shopy.sales.urls', namespace='sales')),
    path('', include('miq.analytics.urls', namespace='analytics')),
    path('', include('miq.staff.urls', namespace='staff')),
    path('', include('miq.core.urls', namespace='miq')),
    path('', views.IndexView.as_view(), name='index'),

]
