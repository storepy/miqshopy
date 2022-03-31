import logging

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from miq.utils import get_session
from miqshop.models import Product, ProductSize

from .models import Cart, OrdersSetting, OrderItem
from .serializers import CartSerializer, CustomerSerializer, OrderItemSerializer

logger = logging.getLogger(__name__)
loginfo = logger.info
logerror = logger.error
User = get_user_model()


class CartViewSetMixin:
    def get_setting(self):
        return OrdersSetting.objects.filter(site=get_current_site(self.request)).first()


class CartViewset(CartViewSetMixin, viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    parser_classes = (JSONParser, )
    permission_classes = []
    authentication_classes = []
    renderer_classes = [JSONRenderer]

    @action(methods=['patch', 'delete'], detail=True, url_path=r'item/(?P<item_slug>[\w-]+)')
    def item(self, request, *args, item_slug=None, ** kwargs):
        if not item_slug:
            raise serializers.ValidationError({'item': 'Slug required'})

        item = OrderItem.objects.filter(slug=item_slug)
        if not item.exists():
            raise serializers.ValidationError({'item': 'Invalid slug'})

        item = item.first()
        if request.method == 'DELETE':
            item.delete()

        if request.method == 'PATCH':
            rdata = request.data
            size = ProductSize.objects.filter(slug=rdata.get('size')).first()
            if size != item.size:
                item.size = size
                item.save()

        return self.retrieve(request, *args, **kwargs)

    @action(methods=['post'], detail=False, url_path='items')
    def items(self, request, *args, **kwargs):
        r_data = request.data
        prod_meta_slug = r_data.get('prod_meta_slug')
        if not prod_meta_slug:
            raise serializers.ValidationError({'product': 'Slug required'})

        prod = Product.objects.published().filter(meta_slug=prod_meta_slug)
        if not prod.exists():
            raise serializers.ValidationError({'product': 'Invalid slug'})

        prod = prod.first()
        session = self.get_session()
        cart_slug = r_data.get('cart_slug', session.get('_car_id'))
        cart = Cart.objects.filter(slug=cart_slug)
        if not cart.exists():
            cart = self.create_cart()
        else:
            cart = cart.first()

        cart.products.add(prod, through_defaults={
            'size': ProductSize.objects.filter(slug=r_data.get('size')).first()})

        return Response(CartSerializer(cart).data)

    @action(methods=['post', 'patch'], detail=True, url_path=r'customer')
    def customer(self, request, *args, **kwargs):
        cart = self.get_object()
        cart_id = cart.id
        customer = cart.customer
        rdata = request.data

        if request.method == 'POST':
            if customer:
                logerror(
                    f'Cannot add new customer to cart[{cart_id}] '
                    f'with customer[{customer.id}]'
                )
                raise serializers.ValidationError(
                    {'customer': 'This cart is invalid'}, code='invalid')

            loginfo(f'Creating new customer: {rdata}')
            ser = CustomerSerializer(data=rdata)
            ser.is_valid(raise_exception=True)
            cust = self.perform_create_customer(ser)

            cart.customer = cust
            cart.save()
            loginfo(f'Added customer[{cust.id}] to cart[{cart.id}]')

        if customer and customer.slug != rdata.get('cust_slug'):
            raise serializers.ValidationError({'customer': 'No match'}, code='invalid')

        if request.method == 'PATCH':
            pass

        return self.retrieve(request, *args, **kwargs)

    def perform_create_customer(self, cust_ser):
        cust = cust_ser.save()
        cust_id = cust.id
        loginfo(f'Created new customer[{cust_id}]')

        session = self.get_session()
        session['_cus_id'] = f'{cust_id}'
        session.modified = True
        loginfo(f'Added customer id[{cust_id}] to session')
        return cust

    @action(methods=['post'], detail=False, url_path=r'_customer')
    def _customer(self, request, *args, **kwargs):
        cart = None
        cart_slug = request.data.get('cart_slug')
        if cart_slug and (_cart := Cart.objects.filter(slug=cart_slug)) and _cart.exists():
            cart = _cart.first()
            if cart.customer:
                logerror(
                    f'Cannot add new customer to cart[{cart.id}] '
                    f'with customer[{cart.customer.id}]'
                )
                raise serializers.ValidationError(
                    {'customer': 'This cart is invalid'}, code='invalid')

        loginfo(f'Creating new customer: {request.data}')

        ser = CustomerSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        staff_slug = request.data.get('staff_slug')
        data = {}
        if staff_slug and (staff := User.objects.filter(slug=staff_slug)) and staff.exists():
            data['added_by'] = staff.first()

        cust = ser.save(**data)

        if cart:
            cart.customer = cust
            cart.save()

        return Response(ser.data)

    def perform_create(self, serializer):
        self.create_cart(serializer)

    def create_cart(self, serializer=None):
        data = {'setting': self.get_setting()}
        staff_slug = self.request.data.get('staff_slug')
        is_staff = False
        if staff_slug and (staff := User.objects.filter(slug=staff_slug).first()):
            data['added_by'] = staff
            is_staff = True

        if serializer:
            return serializer.save(**data)

        cart = Cart.objects.create(**data)
        if not is_staff:
            session = get_session(self.request)
            session['_car_id'] = f'{cart.slug}'
            session.modified = True
            loginfo(f'Added cart id[{cart.id}] to session[{session.session_key}]')

        return cart

    def list(self, *args, **kwargs):
        return Response({})

    def get_session(self):
        return get_session(self.request)
