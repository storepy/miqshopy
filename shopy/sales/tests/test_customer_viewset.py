# from django.test import TransactionTestCase

from rest_framework import status
from rest_framework.test import APITransactionTestCase

from shopy.sales.models import Customer


from .utils import SalesMixin


class Mixin(SalesMixin):
    pass


class TestCustomerViewSet(Mixin, APITransactionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.site.save()
        self.user = self.create_staffuser(self.username, self.password)
        self.client.login(username=self.username, password=self.password)

    def test_list(self):
        Customer.objects.create(first_name='John', last_name='Candide', phone='1234567890')
        Customer.objects.create(first_name='Jean-Michel', last_name='Doe', phone='123456789')
        Customer.objects.create(first_name='Rock', last_name='Gilles', phone='123422789')

        self.add_user_perm(self.user, 'view_customer')
        path = self.get_customer_list_path()
        r = self.client.get(path)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEquals(r.data['count'], 3)

        r = self.client.get(f'{path}', {'q': 'jo'})
        self.assertEquals(r.data['count'], 0)

        r = self.client.get(f'{path}', {'q': 'michel'})
        self.assertEquals(r.data['count'], 1)

        r = self.client.get(f'{path}', {'q': '1234567'})
        self.assertEquals(r.data['count'], 2)

    def test_create_update_delete(self):
        path = self.get_customer_list_path()

        # test create
        data = {'first_name': 'John', 'last_name': 'Doe', 'email': 'jdoe', }
        r = self.client.post(path, data=data, format='json')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

        self.add_user_perm(self.user, 'add_customer')
        r = self.client.post(path, data=data, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', r.data)

        data.update({'email': 'jdoe@gmail.com'})
        r = self.client.post(path, data=data, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', r.data)

        # email not really required
        del data['email']
        data.update({'phone': '1234567890'})

        r = self.client.post(path, data=data, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        # duplicate phone
        s = self.client.post(path, data=data, format='json')
        self.assertEqual(s.status_code, status.HTTP_400_BAD_REQUEST)

        # first/last name min length
        s = self.client.post(path, data={**data, 'first_name': 'J'}, format='json')
        self.assertEqual(s.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', s.data)
        s = self.client.post(path, data={**data, 'last_name': 'J'}, format='json')
        self.assertEqual(s.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_name', s.data)

        slug = r.data['slug']
        self.assertEquals(r.data['name'], 'John Doe')
        self.assertIsNone(r.data['user'])
        self.assertIsNone(r.data['email'])

        self.assertEquals(
            Customer.objects.get(slug=slug).added_by,
            self.user
        )

        self.add_user_perm(self.user, 'change_customer')
        changepath = self.get_customer_detail_path(slug)

        r = self.client.patch(changepath, data={'last_name': 'Gainyo'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEquals(r.data['name'], 'John Gainyo')

        self.add_user_perm(self.user, 'delete_customer')
        r = self.client.delete(changepath)
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
