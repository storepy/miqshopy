from django.urls import reverse_lazy


from shopy.store.tests.utils import ShopMixin


class SalesMixin(ShopMixin):
    def get_order_list_path(self):
        return reverse_lazy('sales:order-list')

    def get_order_detail_path(self, slug):
        return reverse_lazy('sales:order-detail', args=[slug])

    def get_cart_place_path(self, slug):
        return reverse_lazy('sales:cart-place', args=[slug])

    def get_cart_post_item_path(self, slug, product_meta_slug):
        return reverse_lazy('sales:cart-post-item', args=[slug, product_meta_slug])

    def get_cart_detail_path(self, slug):
        return reverse_lazy('sales:cart-detail', args=[slug])

    def get_cart_list_path(self):
        return reverse_lazy('sales:cart-list')

    def get_customer_list_path(self):
        return reverse_lazy('sales:customer-list')

    def get_customer_detail_path(self, slug):
        return reverse_lazy('sales:customer-detail', args=[slug])
