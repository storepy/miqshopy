
from rest_framework import viewsets, serializers
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action


from shopy.store.models import Product
from miq.staff.mixins import LoginRequiredMixin
from miq.core.permissions import DjangoModelPermissions

from ..models import Cart, Order, Customer, OrderItem
from ..serializers import CartSerializer, OrderSerializer, CustomerSerializer


class Mixin(LoginRequiredMixin):
    lookup_field = 'slug'
    parser_classes = (JSONParser, )
    permission_classes = (IsAdminUser, DjangoModelPermissions)


class CustomerViewset(Mixin, viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        q = params.get('q')
        if q:
            qs = qs.find(q)

        return qs


def add_item_to_cart(order, product_slug, size_slug, quantity=1):

    if OrderItem.objects.filter(order=order, product__meta_slug=product_slug, size__slug=size_slug).exists():
        return

    if not product_slug:
        raise serializers.ValidationError({'product': 'Slug required'})

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


class CartViewset(Mixin, viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(methods=['post'], detail=True, url_path=r'place')
    def place(self, request, *args, ** kwargs):
        self.get_object().place()
        return self.retrieve(request, *args, ** kwargs)

    @action(methods=['post'], detail=True, url_path=r'products')
    def post_items(self, request, *args, ** kwargs):
        """ Add products to cart """

        r_data = request.data
        if not(isinstance(r_data, list)):
            raise serializers.ValidationError({'data': 'invalid1'})

        cart = self.get_object()
        for data in r_data:
            product_slug = data.pop('product_slug', None)
            if not product_slug:
                raise serializers.ValidationError({'data': 'invalid2'})

            self.add_item(cart, product_slug, data)

        return self.retrieve(request, *args, **kwargs)

    @action(methods=['post'], detail=True, url_path=r'product/(?P<product_slug>[\w-]+)')
    def post_item(self, request, *args, product_slug: str = None, ** kwargs):
        """ Add product to cart """

        self.add_item(self.get_object(), product_slug, request.data)

        # size_slug = request.data.pop('size', None)

        # qs = cart.items.filter(product__meta_slug=product_slug, size__slug=size_slug)
        # if not qs.exists():
        #     add_item_to_cart(
        #         cart, product_slug, size_slug,
        #         quantity=request.data.pop('quantity', 1),
        #     )

        return self.retrieve(request, *args, **kwargs)

    def add_item(self, cart, product_slug, request_data):
        size_slug = request_data.pop('size', None)

        qs = cart.items.filter(product__meta_slug=product_slug, size__slug=size_slug)
        if not qs.exists():
            add_item_to_cart(
                cart, product_slug, size_slug,
                quantity=request_data.pop('quantity', 1),
            )

    @action(methods=['post', 'patch', 'delete'], detail=True, url_path=r'item/(?P<item_slug>[\w-]+)')
    def item(self, request, *args, item_slug: str = None, **kwargs):
        order = self.get_object()

        item = order.items.filter(slug=item_slug)
        if not item.exists():
            raise serializers.ValidationError({'item': 'Not found'})

        item = item.first()
        if request.method == 'DELETE':
            item.delete()
            return self.retrieve(request, *args, **kwargs)

        # product = Product.objects.published().filter(slug=product_slug)
        # if not product.exists():
        #     raise serializers.ValidationError({'product': 'Not found'})

        # product = product.first()
        # size = product.sizes.filter(slug=request.data.get('size'))
        # if not size.exists():
        #     raise serializers.ValidationError({'size': 'Size required'})

        # size = size.first()

        # if request.method == 'POST':
        #     add_item_to_cart(order, product_slug, request.data.get('size'))
        #     return self.retrieve(request, *args, **kwargs)

        # item.size = size
        # item.quantity = request.data.get('qty', 1)
        # item.save()

        return self.retrieve(request, *args, **kwargs)


class OrderViewset(CartViewset):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
