import time
from django.test import TestCase
from django.test import LiveServerTestCase
from django.urls import reverse_lazy

from shopy.store.models import ShopSetting
from  miq.tests.utils import get_or_create_site
from .utils import ShopMixin



class TestProductView(ShopMixin, LiveServerTestCase):
    port: int = 8001

    def setUp(self) -> None:
        super().setUp()
        site = get_or_create_site()
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
