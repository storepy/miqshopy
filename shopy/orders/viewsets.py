
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAdminUser

from miq.staff.mixins import LoginRequiredMixin
from miq.core.permissions import DjangoModelPermissions


from .models import Cart, Order, Customer

from .serializers import CartSerializer, OrderSerializer, CustomerSerializer


class Mixin(LoginRequiredMixin):
    lookup_field = 'slug'  # type: str
    parser_classes = (JSONParser, )
    permission_classes = (IsAdminUser, DjangoModelPermissions)


class CustomerViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    lookup_field = 'slug'  # type: str
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    parser_classes = (JSONParser, )
    permission_classes = (IsAdminUser, DjangoModelPermissions)


class CartViewset(Mixin, viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class OrderViewset(Mixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
