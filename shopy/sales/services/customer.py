import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ..models import Customer
from ..models.managers import CustomerQuerySet


log = logging.getLogger(__name__)
CUSTOMER_SESSION_KEY = getattr(settings, 'CUSTOMER_SESSION_KEY', '_cus')

cache = {}


class CustomerFilterSerializer(serializers.Serializer):
    q = serializers.CharField(required=False)


def customer_get_from_request_or_create(request: HttpRequest, /, data: dict):
    """
    Get a customer from request.
    If customer is not found, and data is supplied, get or create a new one.
    Raise ValidationError if customer is not found and data is not supplied.
    """

    if cus := customer_get_from_request(request):
        log.info(f'[{cus.pk}] Customer found from request')
        return cus

    if not isinstance(data, dict):
        raise serializers.ValidationError({'customer': _('Invalid data')})

    if (phone := data.get('phone')) and (qs := Customer.objects.filter(phone=phone)) and qs.exists():
        cus = qs.first()
        log.info(f'[{cus.pk}] Customer found by phone')
        return cus

    return customer_create(data=data)


def customer_get_from_request(request: HttpRequest, /) -> Customer:
    """
    Get a customer from request cookies or session.
    If customer is not found, return None.
    """

    cus_slug = request.COOKIES.get(CUSTOMER_SESSION_KEY)
    if not cus_slug:
        cus_slug = request.session.get(CUSTOMER_SESSION_KEY)
    if not cus_slug:
        return None

    if cus_slug in cache:
        return cache[cus_slug]

    if (qs := Customer.objects.filter(slug=cus_slug)) and qs.exists():
        cus = qs.first()
        cache[f'{cus_slug}'] = cus
        return cus

    return None


def customer_save_to_request(customer: Customer, request: HttpRequest, response: HttpResponse):
    """
    Save a customer to request session and response cookies
    Save customer instance to cache
    """

    slug = f'{customer.slug}'
    response.set_cookie(CUSTOMER_SESSION_KEY, slug)

    if request.session.get(CUSTOMER_SESSION_KEY, None) != slug:
        request.COOKIES[CUSTOMER_SESSION_KEY] = slug
        request.session[CUSTOMER_SESSION_KEY] = slug
        request.session.modified = True

    if slug not in cache:
        cache[slug] = customer


def customer_create_by_staff(*, data: dict, creator, **kwargs) -> Customer:
    """
    Create a customer with a staff account. Staff can create a customer for another user.
    data: dict
    user: StaffUser
    request: Request, Optional
    """

    assert creator, 'Creator user is required'
    assert creator.is_staff, 'Only staff can create customers'
    return customer_create(data={**data, 'added_by': creator})


def customer_create(*, data: dict) -> Customer:
    """ Create a new customer """

    class CustomerSerializer(serializers.ModelSerializer):
        class Meta():
            model = Customer
            fields = ('first_name', 'last_name', 'phone', 'email')
            extra_kwargs = {
                'first_name': {'required': True},
                'last_name': {'required': True},
                'phone': {'required': True},
            }

    ser = CustomerSerializer(data=data)
    ser.is_valid(raise_exception=True)
    print(data)
    print(ser.validated_data)

    cus = Customer(**ser.validated_data)

    cus.full_clean()
    cus.save()

    log.info(f'[{cus.pk}] Customer created')
    return cus


def customer_delete(*, instance: Customer) -> None:
    """
    Delete a customer. A customer with orders can not be deleted.
    """

    pk = instance.pk
    instance.delete()
    log.info(f'[{pk}] Customer deleted')


def customer_get_last_cart(customer):
    """
    Get a customer's last cart.
    """

    if not customer:
        return None

    return customer.orders.filter(is_placed=False).first()


def customer_qs(*, filters: dict = None, **kwargs) -> CustomerQuerySet:
    qs = Customer.objects.all()
    if not filters:
        return qs
    return qs
