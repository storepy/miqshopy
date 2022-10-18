
from django.urls import reverse_lazy
from django.utils.text import slugify
from miq.core.tests.utils import TestMixin

from shopy.store.models import Product, ProductSize, Category


class StoreMixin(TestMixin):

    def add_size_to_product(self, product, name, **kwargs):
        code = kwargs.get('code') or slugify(name)
        ProductSize.objects.create(product=product, name=name, code=code, **kwargs)

    def create_product(self, name, retail_price, published=False, **kwargs):
        name = name or 'A product'
        retail_price = retail_price or 100
        if not published:
            return Product.objects.create(name=name, retail_price=retail_price, **kwargs)

        kwargs['meta_slug'] = kwargs.get('meta_slug') or 'a-product'
        kwargs['meta_title'] = kwargs.get('meta_title') or 'A product'
        p = Product.objects.create(
            category=self.create_category('A category', published=True),
            name=name, retail_price=retail_price, **kwargs
        )
        p.publish()
        return p

    def create_category(self, name, published=False, **kwargs):
        name = name or 'A category'
        if not published:
            return Category.objects.create(name=name, **kwargs)

        kwargs['meta_slug'] = kwargs.get('meta_slug') or 'a-category'
        kwargs['meta_title'] = kwargs.get('meta_title') or 'A category'
        c = Category.objects.create(name=name, **kwargs)
        c.publish()
        return c

    def get_cart_path(self, *, slug=None):
        if slug:
            return reverse_lazy('shop:cart_update', args=[slug])
        return reverse_lazy('store:cart', args=[])

    def get_product_category_path(self, slug):
        return reverse_lazy('store:product-category', args=[slug])

    def get_product_page_path(self, slug):
        return reverse_lazy('store:product-page', args=[slug])

    def get_product_detail_path(self, slug):
        return reverse_lazy('store:product-detail', args=[slug])

    def get_product_publish_path(self, slug):
        return reverse_lazy('store:product-publish', args=[slug])

    def get_product_list_path(self):
        return reverse_lazy('store:product-list')

    def get_category_detail_path(self, slug):
        return reverse_lazy('store:category-detail', args=[slug])

    def get_category_publish_path(self, slug):
        return reverse_lazy('store:category-publish', args=[slug])

    def get_category_list_path(self):
        return reverse_lazy('store:category-list')
