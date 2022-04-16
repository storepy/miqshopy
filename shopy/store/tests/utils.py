from django.urls import reverse_lazy

from miq.tests.mixins import TestMixin

from shopy.store.models import Product, ProductPage


class ShopMixin(TestMixin):

    def create_product(self, name='A product', published=False):
        return Product.objects.create(
            name=name,
            page=ProductPage.objects.create(
                site=self.site, title=name, is_published=published)
        )

    def get_cart_path(self, *, slug=None):
        if slug:
            return reverse_lazy('shop:cart_update', args=[slug])
        return reverse_lazy('shop:cart', args=[])

    def get_product_category_path(self, slug):
        return reverse_lazy('shop:product-category', args=[slug])

    def get_product_page_path(self, slug):
        return reverse_lazy('shop:product-page', args=[slug])

    def get_product_detail_path(self, slug):
        return reverse_lazy('shop:product-detail', args=[slug])

    def get_product_list_path(self):
        return reverse_lazy('shop:product-list')

    def get_category_detail_path(self, slug):
        return reverse_lazy('shop:category-detail', args=[slug])

    def get_category_list_path(self):
        return reverse_lazy('shop:category-list')
