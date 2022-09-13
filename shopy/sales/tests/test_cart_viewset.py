# from pprint import pprint

from rest_framework import status
from rest_framework.test import APITestCase

from shopy.sales.models.order import Cart

from .utils import SalesMixin


class Mixin(SalesMixin):
    pass


class TestCartViewSet(Mixin, APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.site.save()
        self.user = self.create_staffuser(self.username, self.password)
        self.client.login(username=self.username, password=self.password)

    def test_mark_paid(self):
        # is placed
        # is not delivered
        # after payment check items quantity has decreased
        # test is no longer a cart
        pass

    def test_place(self):
        self.add_user_perm(self.user, 'add_cart')
        self.add_user_perm(self.user, 'change_cart')
        self.assertTrue(self.user.has_perm('sales.change_cart'))

        cart = Cart.objects.create()
        path = self.get_cart_place_path(cart.slug)

        # no cart items
        r = self.client.post(path)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # no customer
        # is already paid

    def test_create_update_delete(self, ):
        self.add_user_perm(self.user, 'add_cart')
        path = self.get_cart_list_path()

        r = self.client.post(path, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED,)

        slug = r.data['slug']
        self.assertEquals(Cart.objects.get(slug=slug).added_by, self.user)

        # invalid product meta slug
        item_path = self.get_cart_post_item_path(slug, 'product-meta-1')

        p = self.create_product('A product', 10, published=True)
        self.assertTrue(p.is_published)

        self.add_size_to_product(p, 'small')
        self.add_size_to_product(p, 'large', quantity=0)
        self.assertEquals(p.sizes.count(), 2)

        s = p.sizes.filter(code='small').first()
        self.assertEquals(s.quantity, 1)

        item_path = self.get_cart_post_item_path(slug, p.meta_slug)
        data = {'quantity': 1}
        r = self.client.post(item_path, data=data, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        data.update({'size': s.slug})
        r = self.client.post(item_path, data=data, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn(p.meta_slug, r.data['products'])
        self.assertEquals(s.slug, r.data['items'][0]['size'])

        r = self.client.post(
            item_path,
            data={'size': p.sizes.filter(code='large').first().slug},
            format="json")

        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # check items are deleted when cart is deleted

        # raise Exception(r.data)
