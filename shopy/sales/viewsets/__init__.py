import logging
from decimal import Decimal
from django.http import JsonResponse

from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAdminUser

from miq.staff.mixins import LoginRequiredMixin
from miq.core.permissions import DjangoModelPermissions


from ..models import Cart, Order
from ..services import cart_add_item, cart_delete_item
from ..services import customer_qs, customer_delete, customer_create_by_staff, CustomerFilterSerializer
from ..serializers import OrderSerializer, CustomerSerializer, get_cart_serializer_class, DiscountSerializer

log = logging.getLogger(__name__)


class Mixin(LoginRequiredMixin):
    lookup_field: str = 'slug'
    parser_classes = (JSONParser, )
    permission_classes = (IsAdminUser, DjangoModelPermissions)


class CustomerViewset(Mixin, viewsets.ModelViewSet):
    queryset = customer_qs().none()
    serializer_class = CustomerSerializer

    def get_queryset(self):
        filters = CustomerFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)

        data = filters.validated_data
        q = data.pop('q', '')
        qs = customer_qs(filters=data)
        if q:
            if len(q) < 3:
                return qs.none()
            qs = qs.find(q)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        try:
            serializer.instance = customer_create_by_staff(
                data=serializer.validated_data, creator=user, request=self.request
            )
        except Exception as e:
            log.error(f'[{self.request.user.pk}]: User cannot create customer: {e}')
            raise serializers.ValidationError({'customer': 'Can not create customer'})

    def perform_destroy(self, instance):
        try:
            customer_delete(instance=instance)
        except Exception as e:
            log.error(f'[{instance.id}] {e}')
            raise serializers.ValidationError({'customer': 'Can not delete customer'})


class CartViewsMixin(Mixin):
    pass


class CartViewset(CartViewsMixin, viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = get_cart_serializer_class(
        extra_fields=('customer', 'notes', 'dt_delivery'),
        extra_read_only_fields=(
            'slug', 'customer_name', 'customer_data', 'is_placed',
            'items', 'products', 'discounts',
            'subtotal', 'total', 'created', 'updated')
    )

    @action(methods=['post'], detail=True, url_path=r'pay')
    def mark_paid(self, request, *args, ** kwargs):

        obj = self.get_object()
        if not obj.is_placed:
            raise serializers.ValidationError({'cart': 'Not placed'})

        try:
            obj.mark_paid()
        except Exception as e:
            raise serializers.ValidationError({'cart': str(e)})

        return JsonResponse({'status': 'ok'})

    @action(methods=['post'], detail=True, url_path=r'place')
    def place(self, request, *args, ** kwargs):

        obj = self.get_object()
        if obj.is_placed:
            raise serializers.ValidationError({'cart': 'Already placed'})

        try:
            obj.place()
        except Exception as e:
            raise serializers.ValidationError({'cart': str(e)})

        return self.retrieve(request, *args, ** kwargs)

    @action(methods=['post'], detail=True, url_path=r'discount')
    def add_discount(self, request, *args, ** kwargs):

        ser = DiscountSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        cart = self.get_object()
        if Decimal(request.data.get('amt')) > cart.get_subtotal():
            raise serializers.ValidationError({'amt': 'Invalid amount'})

        ser.save(order=cart)
        return self.retrieve(request, *args, ** kwargs)

    @action(methods=['delete'], detail=True, url_path=r'discount/(?P<discount_slug>[\w-]+)')
    def delete_discount(self, request, *args, discount_slug=None, ** kwargs):
        discount = self.get_object().discounts.filter(slug=discount_slug)
        if not discount.exists():
            raise serializers.ValidationError({'discount': 'Not found'})

        discount.first().delete()
        return self.retrieve(request, *args, ** kwargs)

    @action(methods=['post'], detail=True, url_path=r'products')
    def post_items(self, request, *args, ** kwargs):
        # raise serializers.ValidationError({'data': 'invalid-01'})
        """ Add products to cart """
        r_data = request.data
        if not (isinstance(r_data, list)):
            raise serializers.ValidationError({'data': 'Invalid data'})

        cart = self.get_object()
        for data in r_data:
            product_slug = data.pop('product_slug', None)
            if not product_slug:
                raise serializers.ValidationError({'data': 'Product slug is required'})

            cart_add_item(cart, data={**data, 'product': product_slug})

        return self.retrieve(request, *args, **kwargs)

    @action(methods=['post'], detail=True, url_path=r'product/(?P<product_slug>[\w-]+)')
    def post_item(self, request, *args, product_slug: str = None, ** kwargs):
        """ Add product to cart """
        cart_add_item(self.get_object(), data={**request.data, 'product': product_slug})
        return self.retrieve(request, *args, **kwargs)

    @action(methods=['delete'], detail=True, url_path=r'item/(?P<item_slug>[\w-]+)')
    def delete_item(self, request, *args, item_slug: str = None, **kwargs):
        """ Delete item from cart """
        cart_delete_item(self.get_object(), item_slug=item_slug)
        return self.retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return get_cart_serializer_class(
                request=self.request,
                extra_read_only_fields=('is_placed', 'customer', 'subtotal', 'total', 'created', 'updated')
            )
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class OrderViewset(CartViewsMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(methods=['post'], detail=True, url_path=r'deliver')
    def mark_delivered(self, request, *args, ** kwargs):
        try:
            self.get_object().mark_delivered()
        except Exception:
            raise serializers.ValidationError({'order': 'Something went wrong'})

        return self.retrieve(request, *args, ** kwargs)

    def get_queryset(self):
        if self.action in ('list', 'destroy'):
            return Order.objects.none()

        return super().get_queryset()
