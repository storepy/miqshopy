import logging

from django.contrib.sites.middleware import CurrentSiteMiddleware
from django.contrib.sites.shortcuts import get_current_site

from miq.core.utils import get_session

from ..sales.models import Cart
from ..sales.api import APICartSerializer

from .utils import get_customer_from_session

logger = logging.getLogger(__name__)
loginfo = logger.info
logerror = logger.error


def get_customer(request):
    if not hasattr(request, '_cached_customer'):
        request._cached_customer = get_customer_from_session(request)
    return request._cached_customer


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
        session = get_session(request)
        if session.session_key and (cart_slug := session.get('_cart')) and (cart := Cart.objects.filter(slug=cart_slug)) and cart.exists():
            cart = cart.first()
            obj = response.context_data.get('object')
            if obj:
                loginfo(f'ProductView[{obj.id}]')

            sD.update({
                'cart': APICartSerializer(cart).data
            })

            loginfo(f'Session cart[{cart.id}]')

        return response
