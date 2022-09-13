import shutil
from decimal import Decimal

from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from miq.core.tests.utils import get_temp_img

from .utils import ShopMixin

from shopy.store.models import Product, Category

TEST_MEDIA_DIR = 'test_media'


class Mixin(ShopMixin):

    def tearDown(self):
        try:
            shutil.rmtree(TEST_MEDIA_DIR)
        except Exception:
            pass


@override_settings(MEDIA_ROOT=(TEST_MEDIA_DIR))
class TestStoreProductViewSet(Mixin, APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.site.save()
        self.user = self.create_staffuser(self.username, self.password)
        self.client.login(
            username=self.username,
            password=self.password
        )

    def test_publish(self):
        self.add_user_perm(self.user, 'add_product')
        self.add_user_perm(self.user, 'change_product')
        self.add_user_perm(self.user, 'change_category')

        p = Product.objects.create(name='A product')
        self.assertFalse(p.is_published)

        slug = p.slug
        path = self.get_product_detail_path(slug)
        pub_path = self.get_product_publish_path(slug)

        r = self.client.patch(pub_path, {'is_published': False}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertFalse(r.data['is_published'])

        # cant publish without a published category
        self.assertIsNone(p.category)
        self.assertEqual(
            self.client.patch(pub_path, {'is_published': True}, format="json").status_code,
            status.HTTP_400_BAD_REQUEST
        )

        c = Category.objects.create(name='A category', meta_slug='a-category', meta_title='A category')
        r = self.client.patch(path, {'category': c.slug}, format="json")
        self.assertEqual(r.data['category'], f'{c.slug}')

        self.assertEqual(
            self.client.patch(pub_path, {'is_published': True}, format="json").status_code,
            status.HTTP_400_BAD_REQUEST
        )

        c.publish()

        # can't publish without retail price
        self.assertEqual(
            self.client.patch(pub_path, {'is_published': True}, format="json").status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.client.patch(path, {'retail_price': 10}, format="json").status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(Product.objects.get(slug=slug).retail_price, Decimal(10))

        # can't publish without meta title and meta slug
        self.assertIsNone(p.meta_slug)
        self.assertIsNone(p.meta_title)
        self.assertEqual(
            self.client.patch(pub_path, {'is_published': True}, format="json").status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.client.patch(path, {'meta_slug': 'a-meta-title', 'meta_title': 'My prod'}, format="json").status_code,
            status.HTTP_200_OK
        )
        p = Product.objects.get(slug=slug)
        self.assertEqual(p.meta_slug, 'a-meta-title')
        self.assertEqual(p.meta_title, 'My prod')

        r = self.client.patch(pub_path, {'is_published': True}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(r.data['is_published'])

    def test_add_images(self):
        self.add_user_perm(self.user, 'add_image')
        self.add_user_perm(self.user, 'change_product')

        p = Product.objects.create(name='A product')
        self.assertIsNone(p.cover)

        path = self.get_product_detail_path(p.slug)

        # add cover
        r = self.client.post(self.get_staff_img_list_path(), {'src': get_temp_img()},)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = self.client.patch(path, {'cover': r.data['slug']}, format="json")

        self.assertIn('slug', r.data['cover_data'])

        r = self.client.post(self.get_staff_img_list_path(), {'src': get_temp_img()},)
        img_slug = r.data['slug']
        r = self.client.post(self.get_staff_img_list_path(), {'src': get_temp_img()},)
        img_slug2 = r.data['slug']

        # add image to product
        r = self.client.patch(path, {'images': [img_slug, img_slug2]}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data['images_data']), 2)

        # # remove image
        # r = self.client.patch(path, {'images': [img_slug]}, format="json")
        # self.assertEqual(r.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(r.data['images_data']), 1)

    def test_create_update_delete(self):
        path = self.get_product_list_path()

        # test post a product
        data = {'name': 'A product'}

        self.assertEqual(
            self.client.post(path, data, format="json").status_code,
            status.HTTP_403_FORBIDDEN
        )

        # add required permission
        self.add_user_perm(self.user, 'add_product')
        self.assertTrue(self.user.has_perm('store.add_product'))

        r = self.client.post(path, data, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        res_data = r.data
        self.assertEqual(res_data['name'], data['name'])
        self.assertEqual(res_data['meta_title'], data['name'])
        self.assertEqual(res_data['meta_slug'], 'a-product')
        self.assertFalse(res_data['is_published'])
        self.assertEqual(res_data['position'], 1)

        r2 = self.client.post(path, {'name': 'Another product'}, format="json")
        self.assertEqual(r2.data['position'], 2)

        slug = res_data['slug']
        u_path = self.get_product_detail_path(slug)
        r = self.client.patch(u_path, {'name': 'Updated product'}, format="json")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

        self.add_user_perm(self.user, 'change_product')
        r = self.client.patch(u_path, {'name': 'Updated product'}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['name'], 'Updated product')

        # test delete
        r = self.client.delete(u_path)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

        self.add_user_perm(self.user, 'delete_product')
        r = self.client.delete(u_path)
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
