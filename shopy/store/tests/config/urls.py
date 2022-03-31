from django.urls import path, include

urlpatterns = [
    path('', include('miq.core.urls', namespace='miq')),
]
