from rest_framework import status
from rest_framework.test import APITestCase

from shopy.models import CategoryPage
from shopy.tests.utils import ShopMixin


class TestStaffCategoryViewSet(ShopMixin, APITestCase):

    def setUp(self) -> None:
        super().setUp()

        self.site
        self.user = self.create_staffuser(self.username, self.password)
        self.client.login(
            username=self.username,
            password=self.password)

    def test_post_cat(self):
        self.assertEqual(
            self.client.post(
                self.get_category_list_path(), {'name': 'my product'}, format="json"
            ).status_code,
            status.HTTP_403_FORBIDDEN)

        self.add_user_perm(self.user, 'add_category')
        self.assertTrue(self.user.has_perm('shop.add_category'))

        r = self.client.post(
            self.get_category_list_path(), {'name': 'my category'}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(r.data.get('page'))

        page = CategoryPage.objects.filter(shop_category__slug=r.data.get('slug'))
        self.assertTrue(page.exists())

        page = page.first()
        self.assertEqual(page.source, 'shop_category')
        self.assertEqual(page.title, r.data.get('name'))
