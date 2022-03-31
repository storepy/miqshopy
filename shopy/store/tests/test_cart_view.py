from http import HTTPStatus as status

from rest_framework.test import APITestCase

from shopy.tests.utils import ShopMixin


class TestCartView(ShopMixin, APITestCase):
    def setUp(self) -> None:
        self.site
        super().setUp()

    def test_patch(self):
        r = self.post_data({'name': 'Michael', 'number': '12345'})
        cart_slug = r.json().get('slug')
        # print(r.session)

        # cart required: wrong url
        self.assertEqual(
            self.client.patch(self.get_cart_path(), {}, format='json').status_code,
            status.BAD_REQUEST
        )

        # invalid actions
        self.assertEqual(
            self.patch_data(cart_slug, {}).status_code,
            status.BAD_REQUEST
        )
        self.assertEqual(
            self.patch_data(cart_slug, {'action': 'wrong action'}).status_code,
            status.BAD_REQUEST
        )

        data = {'action': 'add'}

        # no slug
        self.assertEqual(
            self.patch_data(cart_slug, data).status_code,
            status.BAD_REQUEST
        )

        # wrong slug
        data.update({'slug': ''})
        self.assertEqual(
            self.patch_data(cart_slug, data).status_code,
            status.BAD_REQUEST
        )

        prod = self.create_product(name='My prod')
        slug_pub = prod.page.slug_public

        data.update({'slug': slug_pub, 'size': 'S'})
        r = self.patch_data(cart_slug, data)
        items = r.json().get('items')
        self.assertEqual(items[0].get('size'), 'S')

        item_slug = items[0].get('item_slug')
        data.update({'slug': item_slug, 'action': 'update', 'size': 'm'})
        self.assertEqual(
            self.patch_data(cart_slug, data).json().get('items')[0].get('size'), 'm'
        )

        data.update({'action': 'delete'})
        self.assertEqual(len(self.patch_data(cart_slug, data).json().get('items')), 0)

        # r = self.patch_data(cart_slug, data)
        # # self.assertEqual(r.status_code, status.BAD_REQUEST)
        # print(r.json())

    def test_post(self):
        # required fields
        data = {}
        self.assertEqual(self.post_data(data).status_code, status.BAD_REQUEST)

        # min lengths
        data.update({'name': 'mi', 'number': 'mi'})
        self.assertEqual(self.post_data(data).status_code, status.BAD_REQUEST)

        # wrong number
        data.update({'name': 'michael', 'number': '12345', })
        # self.assertEqual(self.post_data(data).status_code, status.BAD_REQUEST)

        # wrong email
        data.update({'email': 'email'})
        self.assertEqual(self.post_data(data).status_code, status.BAD_REQUEST)

        p = self.create_product()

        data.update({
            'product': p.page.slug_public,
            'size': 'XL',
            'email': 'mich@email.com'
        })
        r = self.post_data(data)
        self.assertEqual(r.status_code, status.CREATED)

        data.update({'size': 'M'})
        r = self.post_data(data)

        res = r.json()
        self.assertIn('slug', res.keys())

        # print(r.__dict__)
        print(res)

    def patch_data(self, slug, data: dict):
        return self.client.patch(self.get_cart_path(slug=slug), data, format="json")

    def post_data(self, data: dict):
        return self.client.post(self.get_cart_path(), data, format="json")
