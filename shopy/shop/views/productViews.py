import csv

from django.http import HttpResponse

from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import serializers

from miq.core.middleware import local
from miq.core.models import SiteSetting
from miq.core.views.generic import ListView, DetailView
from miq.core.serializers import serialize_context_pagination

from ...sales.api import APIProductSerializer
from ...store.models import Product

from ..serializers import category_to_dict, get_category_url
from ..utils import product_to_jsonld, get_published_categories

from ..services import product_qs, ProductFilterSerializer, product_hit_create, customer_get_from_request

from .mixins import ViewMixin


class ProductView(ViewMixin, DetailView):
    model: Product = Product
    template_name: str = 'shop/product.django.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        product = self.object if hasattr(self, 'object') else self.get_object()
        hit_data = dict(
            product=product,
            customer=customer_get_from_request(request, response=response),
            request=request, response=response,
            # type=ProductHit.TYPE_VIEW
        )

        r = request.GET.get('r')
        if r == '1' and (num := SiteSetting.objects.get(site=get_current_site(request)).whatsapp_number):
            response = redirect(self.get_object().get_whatsapp_link(num, request))
            # hit_data['type'] = ProductHit.TYPE_WHATSAPP

        try:
            product_hit_create(**hit_data)
        except Exception:
            pass

        return response

    def get_object(self, *args, **kwargs):
        p = get_object_or_404(
            product_qs(),
            category__meta_slug=self.kwargs.get('category_meta_slug'),
            meta_slug=self.kwargs.get('meta_slug')
        )

        recent = self.request.session.get('_recent') or []
        if p.meta_slug not in recent:
            recent = [p.meta_slug, *recent[:3]]
            self.request.session['_recent'] = recent
            self.request.session.modified = True

        return p

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        obj = context.get('object')
        if not obj:
            return context

        category = obj.category
        p_data = APIProductSerializer(obj).data

        context['title'] = f"{p_data['price']['amountWithSymbol']} - {obj.meta_title} | {category.name}"
        context['meta_description'] = obj.meta_description
        context['jsonld'] = product_to_jsonld(obj, self.request)

        data = {
            'product': p_data,
            'breadcrumbs': [
                {'label': 'Accueil', 'path': '/'},
                {'label': 'Catalogue', 'path': '/shop/'},
                {'label': obj.category.name, 'path': get_category_url(category)},
            ],
        }

        if (similar := obj.category.products.published().exclude(pk=obj.id).filter(is_oos=False))\
                and similar.exists():
            data['similar'] = [
                APIProductSerializer(item).data for item in similar.order_by('?')[:4]
            ]

        self.update_sharedData(context, data)

        return context


class ProductsView(ViewMixin, ListView):
    model: Product = Product
    template_name: str = 'shop/products.django.html'
    context_object_name: str = 'products'
    paginate_by: int = 12
    page_label: str = None

    # TODO: Stage
    queryset = Product.objects.published()

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        context[
            'meta_description'] = f"Trouvez des bijoux chics, des robes, hauts et autre accessoires stylés pour toute occasion sur {self.request.site.name}."

        breadcrumbs = [{'label': 'Accueil', 'path': '/'}]
        if self.request.GET.get('sale', self.request.GET.get('q')):
            breadcrumbs.append({'label': 'Catalogue', 'path': '/shop/'},)

        data = {
            'object_list': APIProductSerializer(context.get('object_list'), many=True).data,
            'pagination': serialize_context_pagination(self.request, context)
        }

        if self.page_label:
            data['page_label'] = self.page_label

        if self.request.GET.get('sale'):
            data['page_label'] = 'Soldes'

        data.update({
            'breadcrumbs': breadcrumbs,
            'categories': [
                category_to_dict(cat) for cat in get_published_categories()
            ],
        })

        self.update_sharedData(context, data)
        return context

    def get_queryset(self):

        qs = self.queryset.none()
        filters = ProductFilterSerializer(data=self.request.GET)
        if filters.is_valid():
            qs = product_qs(filters=filters.validated_data)

        return qs.order_for_shop()


"""
FB
"""


class FBSerializer(serializers.ModelSerializer):

    def __init__(self, instance=None, **kwargs):
        if not kwargs.get('context', {}).get('request'):
            raise Exception("Request required! -> FBSerializer(instance, context={'request': request, 'size': size})")

        super().__init__(instance, **kwargs)
        # context = {"request": request})

    # https://developers.facebook.com/docs/marketing-api/catalog/reference#supported-fields
    # color, status(active,archived), manufacturer_info,material

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'description', 'price', 'link',
            'availability', 'condition', 'image_link', 'brand',

            # optional
            'sale_price', 'additional_image_link', 'product_type',
            'size', 'gender', 'inventory',
            'item_group_id', 'age_group', 'color',
            'google_product_category',
            'custom_label_0', 'custom_label_1'
        )

    id = serializers.CharField(source='meta_slug', read_only=True)
    title = serializers.CharField(source='name', read_only=True)
    description = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()
    additional_image_link = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()
    item_group_id = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    # image_link: 1024 x 1024/1200 x 628,
    # 20 max/https://www.fb.com/t_shirt_2.jpg,https://www.fb.com/t_shirt_3.jpg

    image_link = serializers.SerializerMethodField()
    google_product_category = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    inventory = serializers.SerializerMethodField()
    condition = serializers.CharField(source='get_condition', read_only=True)
    availability = serializers.CharField(source='get_availability', read_only=True)
    age_group = serializers.SerializerMethodField()

    # Use for filtering products to sets
    custom_label_0 = serializers.SerializerMethodField()
    custom_label_1 = serializers.CharField(source='category.name', read_only=True)
#

    def get_custom_label_0(self, inst):
        cat = inst.category

        if cat.parent:
            return cat.parent.name
        return cat.name

    def get_age_group(self, inst):
        """
        The age group the item is targeted towards. Accepted values: adult, all ages, teen, kids, toddler, infant, newborn.
        """

        return 'adult'

    def get_google_product_category(self, inst):
        if (cat := getattr(inst.category, 'google_product_category', None)) and isinstance(cat, str):
            return cat
        return "Clothing & Accessories > Clothing > Dresses"

    def get_item_group_id(self, inst):
        size = self.context.get('size')
        if not size:
            return
        return inst.meta_slug

    def get_description(self, inst):
        if inst.is_oos:
            return "Ce produit n'est plus disponible"

        txt = ''
        sizes = inst.sizes.exclude(code='onesize').filter(quantity__gt=0)
        if sizes.count() > 0:
            for size in sizes.all():
                txt += f'{size.code} '.upper()

        if txt:
            txt = f'Disponible en tailles: {txt}'

        return txt or inst.description

    def get_inventory(self, inst):
        size = self.context.get('size')
        if not size:
            return
        return size.quantity

    def get_gender(self, inst):
        return 'female'

    def get_color(self, inst):
        color = inst.attributes.filter(name__in=['color', 'couleur'])
        if not color.exists():
            return
        return color.first().value

    def get_size(self, inst):
        size = self.context.get('size')
        if not size:
            return
        return f'{size.name}'

    def get_price(self, inst):
        if inst.is_on_sale:
            return self.format_price(inst.retail_price)
        return self.format_price(inst.get_price())

    def get_sale_price(self, inst):
        if inst.is_on_sale:
            return self.format_price(inst.get_price())

    def format_price(self, price):
        site = local.site
        if site and (s := site.shopy):
            return f'{price} {s.currency}'
#

    def get_link(self, inst):
        return f'{inst.path(request=self._request)}?utm_campaign=fbshop'

    def get_image_link(self, inst):
        if inst.cover:
            return self.format_img_link(inst.cover)

    def get_additional_image_link(self, inst):
        if inst.images.exists():
            link = ''.join([
                f'{self.format_img_link(i)},' for i in inst.images.only('src')
            ])
            return link[:-1]

    def format_img_link(self, img):
        return self._request.build_absolute_uri(img.src.url)

    def get_product_type(self, inst):
        return 2271

    def get_brand(self, inst):
        site = getattr(local, 'site')
        if site:
            return site.name

    @property
    def _request(self):
        return self._context.get('request')


class ProductsFbDataFeed(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fb.csv"'

        writer = csv.DictWriter(response, fieldnames=FBSerializer.Meta.fields)
        writer.writeheader()

        qs = product_qs().exclude(is_explicit=True)
        for product in qs:
            data = FBSerializer(product, context={"request": request}).data

            sizes = product.sizes
            if not sizes.exists():
                writer.writerow(data)
                continue

            for size in sizes.all():
                item = {
                    **FBSerializer(product, context={"request": request, 'size': size}).data,
                    'id': size.slug,
                    'availability': size.get_availability(),

                }
                writer.writerow(item)

        return response
