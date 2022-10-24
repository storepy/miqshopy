import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from ...store.models import Product

from ..serializers import OrderItemSerializer, CustomerSerializer
from ..models import Cart, OrderItem, Customer

from .serializers import APICartSerializer

logger = logging.getLogger(__name__)
loginfo = logger.info
logerror = logger.error


def add_item_to_cart(order, product_slug, size_slug, quantity=1):

    if not product_slug:
        raise serializers.ValidationError({'product': 'Slug required'})

    if not size_slug:
        raise serializers.ValidationError({'size': 'Slug required'})

    if OrderItem.objects.filter(order=order, product__meta_slug=product_slug, size__slug=size_slug).exists():
        return

    product = Product.objects.published().filter(meta_slug=product_slug).exclude(is_oos=True)
    if not product.exists():
        raise serializers.ValidationError({'product': 'Not found'})

    product = product.first()
    size = product.sizes.filter(slug=size_slug, quantity__gt=0)
    if not size.exists():
        raise serializers.ValidationError({'size': 'Not found'})

    size = size.first()
    # check size availability

    return OrderItem.objects.create(
        order=order, product=product, size=size, quantity=quantity
    )


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

    return Response(APICartSerializer(cart).data)


@api_view(['POST'])
@permission_classes([])
def post_orderitem(request, product_slug):
    cart: Cart = get_cart_from_session(request)
    size_slug = request.data.pop('size', None)  # type: str

    logger.info(f'Adding product[{product_slug}] size[{size_slug}] to cart[{cart.id}]')

    qs = cart.items.filter(product__meta_slug=product_slug, size__slug=size_slug)
    if not qs.exists():
        add_item_to_cart(
            cart, product_slug, size_slug,
            quantity=request.data.pop('quantity', 1),
        )

    if not cart.customer and (data := request.data.pop('customer', None)):
        cart.customer = get_customer_from_session(request, data)
        cart.save()

    return Response(APICartSerializer(cart).data)


def get_cart_from_session(request, /, customer=None):
    cart_slug = request.session.get('_cart')

    if cart_slug:
        cart = Cart.objects.filter(slug=cart_slug)
        if cart.exists():
            cart = cart.first()
        else:
            cart = Cart.objects.create(customer=customer)
            logger.debug('creating cart')
    else:
        cart = Cart.objects.create(customer=customer)

    request.session['_cart'] = f'{cart.slug}'

    return cart


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
                logerror(f'{e}')
                raise serializers.ValidationError({'customer': _('Something went wrong')})

    request.session['_cus'] = f'{cus.slug}'
    return cus
