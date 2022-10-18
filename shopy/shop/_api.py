import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from ...sales.models import Customer, Cart
from ...sales.viewsets import add_item_to_cart
from ...sales.serializers import CustomerSerializer, CartSerializer, OrderItemSerializer

logger = logging.getLogger(__name__)
loginfo = logger.info
logerror = logger.error


@api_view(['POST'])
@permission_classes([])
def patch_cart(request):
    return Response({"message": "Hello, world!"})


# @api_view(['POST'])
# @permission_classes([])
# def post_customer(request):
#     cus = get_customer_from_session(request, request.data)
#     cart = get_cart_from_session(request, customer=cus)

#     return Response(CartSerializer(cart).data)
