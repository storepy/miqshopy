import shutil
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from miq.core.tests.utils import get_temp_img

from .utils import ShopMixin

TEST_MEDIA_DIR = 'test_media'


class Mixin(ShopMixin):

    def tearDown(self):
        try:
            shutil.rmtree(TEST_MEDIA_DIR)
        except Exception:
            pass


@override_settings(MEDIA_ROOT=(TEST_MEDIA_DIR))
class TestStoreCategoryViewSet(Mixin, APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.site
        self.user = self.create_staffuser(self.username, self.password)
        self.client.login(
            username=self.username,
            password=self.password
        )

    def test_create_update_delete(self):
        path = self.get_category_list_path()

        # test post a category
        data = {'name': 'A category'}

        self.assertEqual(
            self.client.post(path, data, format="json").status_code,
            status.HTTP_403_FORBIDDEN
        )

        # add required permission
        self.add_user_perm(self.user, 'add_category')
        self.assertTrue(self.user.has_perm('store.add_category'))

        r = self.client.post(path, data, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        res_data = r.data
        self.assertEqual(res_data['name'], data['name'])
        self.assertEqual(res_data['meta_title'], data['name'])
        self.assertEqual(res_data['meta_slug'], 'a-category')
        self.assertFalse(res_data['is_published'])
        self.assertEqual(res_data['position'], 1)

        r2 = self.client.post(path, {'name': 'Another category'}, format="json")
        self.assertEqual(r2.data['position'], 2)

        slug = res_data['slug']
        u_path = self.get_category_detail_path(slug)
        r = self.client.patch(u_path, {'name': 'Updated category'}, format="json")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

        self.add_user_perm(self.user, 'change_category')
        r = self.client.patch(u_path, {'name': 'Updated category'}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['name'], 'Updated category')

        # add cover image
        self.add_user_perm(self.user, 'add_image')
        r = self.client.post(self.get_staff_img_list_path(), {'src': get_temp_img()},)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        img_slug = r.data['slug']
        r = self.client.patch(u_path, {'cover': img_slug}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('slug', r.data['cover_data'])

        # test publish
        pub_path = self.get_category_publish_path(slug)
        r = self.client.patch(pub_path, {'is_published': True}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(r.data['is_published'])

        r = self.client.patch(pub_path)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertFalse(r.data['is_published'])

        # can't publish a category without a meta title and meta slug
        meta_slug = r.data['meta_slug']

        r = self.client.patch(u_path, {'meta_slug': None, 'meta_title': None}, format="json")
        self.assertIsNone(r.data['meta_slug'])
        self.assertIsNone(r.data['meta_title'])

        r = self.client.patch(pub_path, {'is_published': True}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.patch(u_path, {'meta_slug': meta_slug}, format="json")
        r = self.client.patch(pub_path, {'is_published': True}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.patch(u_path, {'meta_title': 'A brand new title'}, format="json")
        r = self.client.patch(pub_path, {'is_published': True}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        # test delete
        r = self.client.delete(u_path)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

        self.add_user_perm(self.user, 'delete_category')
        r = self.client.delete(u_path)
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
