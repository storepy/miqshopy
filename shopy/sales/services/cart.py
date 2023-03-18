import logging

from django.conf import settings
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from shopy.store.models import Product, ProductSize
from ..models import OrderItem, Cart

from .customer import customer_get_from_request, customer_get_last_cart, customer_get_from_request_or_create

log = logging.getLogger(__name__)

CART_SESSION_KEY = getattr(settings, 'CART_SESSION_KEY', '_cart')
CUSTOMER_SESSION_KEY = getattr(settings, 'CUSTOMER_SESSION_KEY', '_cus')

cache = {}


@transaction.atomic
def cart_get_from_request_or_create(request: HttpRequest, /, data: dict, customer_data: dict):
    """
    Get a cart from request.
    If cart is not found, and data is supplied, get or create a new one.
    Raise ValidationError if cart is not found and data is not supplied.
    """

    cart = cart_get_from_request(request)
    if hasattr(cart, 'pk'):
        log.info(f'[{cart.pk}]: Cart found from request')
        return cart, False

    if (cus := customer_get_from_request(request)) and (cart := customer_get_last_cart(cus)):
        log.info(f'[{cart.pk}]: Cart found from customer last cart')
        return cart, False

    if not isinstance(data, dict) or not isinstance(customer_data, dict):
        raise serializers.ValidationError({'cart': _('Invalid data')})

    cus = customer_get_from_request_or_create(request, data=customer_data)

    return cart_create(data={**data, 'customer': cus.pk}), True


def cart_get_from_request(request, /):
    cart_slug = request.COOKIES.get(CART_SESSION_KEY)
    if not cart_slug:
        cart_slug = request.session.get(CART_SESSION_KEY)
    if not cart_slug:
        return None

    if cart_slug in cache:
        return cache[cart_slug]

    if (qs := Cart.objects.filter(slug=cart_slug)) and qs.exists():
        cart = qs.first()
        cache[f'{cart_slug}'] = cart
        return cart

    return None


def cart_create_by_staff(*, data: dict, creator, **kwargs) -> Cart:
    """
    Create a cart with a staff account. Staff can create carts other users.
    data: dict
    creator: StaffUser
    request: Request, Optional
    """

    assert creator, 'Creator user is required'
    assert creator.is_staff, 'Only staff can create customers'
    return cart_create(data={**data, 'added_by': creator})


def cart_create(*, data: dict) -> Cart:
    """ Create a new cart """

    class CreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Cart
            fields = ('customer',)
            extra_kwargs = {'customer': {'required': True}}

    ser = CreateSerializer(data=data)
    ser.is_valid(raise_exception=True)

    cart = Cart(**ser.validated_data)

    cart.full_clean()
    cart.save()

    log.info(f'[{cart.pk}]: Cart created')
    return cart


def cart_save_to_request(cart: Cart, request: HttpRequest, response: HttpResponse):
    """
    Save a cart to request session and response cookies
    Save cart instance to cache
    """

    slug = f'{cart.slug}'
    response.set_cookie(CART_SESSION_KEY, slug)

    if request.session.get(CART_SESSION_KEY, None) != slug:
        request.COOKIES[CART_SESSION_KEY] = slug
        request.session[CART_SESSION_KEY] = slug
        request.session.modified = True

    if slug not in cache:
        cache[slug] = cart

    log.info(f'[{cart.pk}]: Cart saved to request')


def cart_update_item(cart: Cart, *, item_slug: OrderItem, data: dict) -> OrderItem:
    """ Update an item in cart """

    item = cart.items.filter(slug=item_slug).first()
    if not item:
        raise serializers.ValidationError({'item': 'Not found'})

    class CartUpdateItemSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ('quantity', 'size')
            extra_kwargs = {'size': {'required': True}, }

        size = serializers.SlugRelatedField(slug_field='slug', queryset=ProductSize.objects.filter(quantity__gt=0))

    ser = CartUpdateItemSerializer(item, data=data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()

    log.info(f'[{item.pk}]: Item updated in [{cart.pk}]: cart')
    return item


def cart_add_item(cart: Cart, *, data: dict) -> OrderItem:
    """ Add an item to cart """

    class CartAddItemSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ('product', 'quantity', 'size')
            extra_kwargs = {'product': {'required': True}, 'size': {'required': True}, }

        product = serializers.SlugRelatedField(slug_field='meta_slug', queryset=Product.objects.published().to_cart())
        size = serializers.SlugRelatedField(slug_field='slug', queryset=ProductSize.objects.filter(quantity__gt=0))

    ser = CartAddItemSerializer(data=data)
    ser.is_valid(raise_exception=True)

    product = ser.validated_data['product']

    if cart.items.filter(product=product, size=ser.validated_data['size']).exists():
        raise serializers.ValidationError({'product': _('This item is already in cart')})

    item = ser.save(order=cart, name=product.name, price=product.get_price(), was_sale=product.is_on_sale)

    log.info(f'[{item.pk}]: Item added to [{cart.pk}]: cart')
    return item


def cart_delete_item(cart: Cart, *, item_slug: str):
    """ Delete an item from cart """

    if not (item := cart.items.filter(slug=item_slug).first()):
        raise serializers.ValidationError({'item': _('Not found')})

    pk = item.pk
    item.delete()
    log.info(f'[{pk}]: Item deleted from [{cart.pk}]: cart')

    def delete_item(self, request, *args, item_slug: str = None, **kwargs):
        order = self.get_object()

        item = order.items.filter(slug=item_slug)
        if not item.exists():
            raise serializers.ValidationError({'item': 'Not found'})

        item = item.first()
        if request.method == 'DELETE':
            item.delete()
            return self.retrieve(request, *args, **kwargs)

        return self.retrieve(request, *args, **kwargs)
