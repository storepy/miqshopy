import logging

from django.contrib.sites.middleware import CurrentSiteMiddleware
from django.contrib.sites.shortcuts import get_current_site

from miq.core.utils import get_session

from shopy.sales.models import Cart
from shopy.sales.serializers import CartSerializer

logger = logging.getLogger(__name__)
loginfo = logger.info
logerror = logger.error


class ShopMiddleware(CurrentSiteMiddleware):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        response = self.get_response(request)
        return response

    def process_request(self, request):
        request.site = get_current_site(request)

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
                'cart': CartSerializer(cart).data
            })

            loginfo(f'Session cart[{cart.id}]')

        return response
