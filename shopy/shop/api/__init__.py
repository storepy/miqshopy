
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

# from shopy.store.models import Product
# from ...sales.models import OrderItem

from ...sales.models import Customer, Cart
from ...sales.viewsets import add_item_to_cart
from ...sales.serializers import CustomerSerializer, CartSerializer, OrderItemSerializer


@api_view(['POST'])
@permission_classes([])
def patch_cart(request):
    return Response({"message": "Hello, world!"})


@api_view(['POST'])
@permission_classes([])
def patch_orderitem(request, item_slug):
    cart = get_cart_from_session(request)
    item = cart.items.filter(slug=item_slug).first()
    if not item:
        raise serializers.ValidationError({'item': 'Not found'})
    ser = OrderItemSerializer(item, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()

    return Response(CartSerializer(cart).data)


@api_view(['POST'])
@permission_classes([])
def post_orderitem(request, product_slug):
    cart = get_cart_from_session(request)
    size_slug = request.data.pop('size', None)

    qs = cart.items.filter(product__meta_slug=product_slug, size__slug=size_slug)
    if not qs.exists():
        add_item_to_cart(
            cart, product_slug, size_slug,
            quantity=request.data.pop('quantity', 1),
        )

    if not cart.customer and (data := request.data.pop('customer', None)):
        cart.customer = get_customer_from_session(request, data)
        cart.save()

    return Response(CartSerializer(cart).data)


@api_view(['POST'])
@permission_classes([])
def post_customer(request):
    cus = get_customer_from_session(request, request.data)
    cart = get_cart_from_session(request, customer=cus)

    return Response(CartSerializer(cart).data)


def get_customer_from_session(request, customer_data):
    cus_slug = request.session.get('_cus')
    cus = None
    if cus_slug:
        cus = Customer.objects.filter(slug=cus_slug).first()

    if not cus:
        cus = Customer.objects.filter(phone=customer_data.get('phone', ''))
        if cus.exists():
            cus = cus.first()
        else:
            ser = CustomerSerializer(data=customer_data)
            ser.is_valid(raise_exception=True)

            try:
                cus = ser.save()
            except Exception as e:
                print(e)
                raise serializers.ValidationError({'customer': _('Something went wrong')})

    request.session['_cus'] = f'{cus.slug}'
    return cus


def get_cart_from_session(request, /, customer=None):
    cart_slug = request.session.get('_cart')

    if cart_slug:
        cart = Cart.objects.filter(slug=cart_slug)
        if cart.exists():
            cart = cart.first()
        else:
            cart = Cart.objects.create(customer=customer)
            print('creating cart')
    else:
        cart = Cart.objects.create(customer=customer)

    request.session['_cart'] = f'{cart.slug}'

    return cart
