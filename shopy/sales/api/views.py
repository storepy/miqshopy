import logging

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .serializers import APICartSerializer
from ..services import (
    cart_get_from_request, cart_get_from_request_or_create, cart_save_to_request,
    cart_add_item, cart_update_item,
    customer_save_to_request,
)

__all__ = ('patch_orderitem', 'post_orderitem')


logger = logging.getLogger(__name__)
loginfo = logger.info
logerror = logger.error


@api_view(['POST'])
@permission_classes([])
def patch_orderitem(request, item_slug):
    # todo: change request path and add cart slug, change method to PATCH

    cart = cart_get_from_request(request)
    if not hasattr(cart, 'pk'):
        raise serializers.ValidationError({'cart': 'Not found'})

    cart_update_item(cart, item_slug=item_slug, data=request.data)

    return Response(APICartSerializer(cart).data)


@api_view(['POST'])
@permission_classes([])
def post_orderitem(request, product_slug):

    data = request.data
    customer_data = data.pop('customer', None)
    cart, is_new = cart_get_from_request_or_create(request, data, customer_data)

    cart_add_item(cart, data={**data, 'product': product_slug, })

    res = Response(APICartSerializer(cart).data, status=201 if is_new else 200)
    if is_new:
        customer_save_to_request(cart.customer, request, res)
        cart_save_to_request(cart, request, res)

    return res
