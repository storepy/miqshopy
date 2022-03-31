import csv

from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from miq.core.middleware import local
from miq.core.views.generic import ListView, DetailView
from miq.core.serializers import serialize_context_pagination

from shopy.store.models import Product

from ..serializers import ProductDetailSerializer, ProductListSerializer, get_product_url
from ..serializers import category_to_dict, get_category_url
from ..utils import product_to_jsonld, get_published_categories

from .mixins import ViewMixin


price_ranges = ['5000', '10000', '25000', '50000']


class ProductView(ViewMixin, DetailView):
    model = Product
    template_name = 'shop/product.django.html'

    def get_object(self, *args, **kwargs):
        return get_object_or_404(
            Product.objects.published(),
            category__meta_slug=self.kwargs.get('category_meta_slug'),
            meta_slug=self.kwargs.get('meta_slug')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj = context.get('object')
        if not obj:
            return context

        category = obj.category
        context['title'] = obj.meta_title + f' - {category.name}'
        context['meta_description'] = obj.meta_description
        context['jsonld'] = product_to_jsonld(obj, self.request)

        data = {
            'product': ProductDetailSerializer(obj).data,
            'breadcrumbs': [
                {'label': 'Accueil', 'path': '/'},
                {'label': 'Catalogue', 'path': '/shop/'},
                {'label': obj.category.name, 'path': get_category_url(category)},
            ],
        }

        if (similar := obj.category.products.published().exclude(pk=obj.id))\
                and similar.exists():
            data['similar'] = [
                ProductListSerializer(item).data for item in similar.all()[:4]
            ]

        self.update_sharedData(context, data)

        return context


class ProductsView(ViewMixin, ListView):
    model = Product
    template_name = 'shop/products.django.html'
    context_object_name = 'products'
    paginate_by = 16
    page_label = None

    # TODO: Stage
    queryset = Product.objects.published()\
        .order_by('stage', 'position', '-created', 'name')

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        breadcrumbs = [{'label': 'Accueil', 'path': '/'}]
        if self.request.GET.get('sale', self.request.GET.get('q')):
            breadcrumbs.append({'label': 'Catalogue', 'path': '/shop/'},)

        data = {
            'object_list': ProductListSerializer(context.get('object_list'), many=True).data,
            'pagination': serialize_context_pagination(self.request, context)
        }
        if self.page_label:
            data['page_label'] = self.page_label

        data.update({
            'breadcrumbs': breadcrumbs,
            'categories': [
                category_to_dict(cat) for cat in get_published_categories()
            ],
        })

        self.update_sharedData(context, data)
        return context

    def get_queryset(self):
        qs = self.queryset
        params = self.request.GET
        if (sale := params.get('sale')) and sale == 'all':
            qs = qs.is_on_sale()
            self.page_label = 'Soldes'

        if (q := self.request.GET.get('q')) and q != '':
            qs = qs.by_name(q)

        if (price := self.request.GET.get('price')) and price in price_ranges:
            qs = qs.by_price(price)

        return qs


"""
FB
"""


class FBSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', 'title', 'description', 'price', 'link',
            'availability', 'condition', 'image_link', 'brand',

            # optional
            'sale_price', 'additional_image_link', 'product_type',
            # 'gender',
            # 'item_group_id',
            # 'size',
            # 'google_product_category',
        )

    id = serializers.CharField(source='meta_slug', read_only=True)
    title = serializers.CharField(source='name', read_only=True)
    price = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()
    additional_image_link = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()
    image_link = serializers.SerializerMethodField()
    condition = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

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

    def get_link(self, inst):
        return self._request.build_absolute_uri(get_product_url(inst))

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
        return inst.category.name

    def get_brand(self, inst):
        site = local.site
        if site:
            return site.name

    def get_availability(self, inst):
        if inst.get_quantity() > 0:
            return 'in stock'
        return 'out of stock'

    def get_condition(self, inst):
        return 'new'

    @property
    def _request(self):
        return self._context.get('request')


class ProductsFbDataFeed(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fb.csv"'

        ser = FBSerializer(Product.objects.published(), many=True, context={"request": request})
        header = FBSerializer.Meta.fields

        writer = csv.DictWriter(response, fieldnames=header)
        writer.writeheader()
        for row in ser.data:
            writer.writerow(row)

        return response
