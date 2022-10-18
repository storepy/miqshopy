import time
from django.test import TestCase
from django.test import LiveServerTestCase
from django.urls import reverse_lazy

from selenium import webdriver
from shopy.store.models import ShopSetting

from .utils import ShopMixin


driver_path = '/Users/marqetintl/Dropbox/MIQ/projects/chromedriver'


class TestProductView(ShopMixin, LiveServerTestCase):
    port: int = 8001

    def setUp(self) -> None:
        super().setUp()
        site = self.site.save()
        self.store_settings = ShopSetting.objects
        self.domain = self.live_server_url

    def test_products_view(self):
        self.assertTrue(ShopSetting.objects.filter(site=self.site).exists())
        time.sleep(3000)
        # r = requests.get(self.domain)
        # self.assertEquals(r.status_code, 200)

        # self.get_user()
        # with webdriver.Chrome(driver_path) as driver:
        #     driver.get(f'{self.domain}/shop/')
        #     driver.save_screenshot('screenshot.png')

        raise
