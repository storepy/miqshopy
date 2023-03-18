import logging
from django.conf import settings
from django.contrib.sites.middleware import CurrentSiteMiddleware
from django.contrib.sites.shortcuts import get_current_site

from shopy.sales.models import Cart
from shopy.sales.api import APICartSerializer

from .utils import get_customer_from_session


logger = logging.getLogger(__name__)
loginfo = logger.info
logerror = logger.error


CART_SESSION_KEY = getattr(settings, 'CART_SESSION_KEY', '_cart')


def get_customer(request):
    if not hasattr(request, '_cached_customer'):
        request._cached_customer = get_customer_from_session(request)
    return request._cached_customer


def get_cart(request):
    slug = request.COOKIES.get(CART_SESSION_KEY)
    if not slug:
        slug = request.session.get(CART_SESSION_KEY)

    if not slug:
        return None
    return Cart.objects.filter(slug=slug).first()


class ShopMiddleware(CurrentSiteMiddleware):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.site = get_current_site(request)
        request.customer = get_customer(request)

        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_template_response(self, request, response):
        ctx = response.context_data
        if not ctx:
            return response

        # SHARED DATA

        if 'sharedData' not in ctx.keys():
            ctx['sharedData'] = {}

        sD = ctx.get('sharedData')

        cart = get_cart(request)
        if hasattr(cart, 'pk'):
            sD['cart'] = APICartSerializer(cart).data

        return response
