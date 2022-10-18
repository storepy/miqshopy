import os
from django.test import LiveServerTestCase

from selenium import webdriver

from miq.core.tests.utils import TestMixin
from miq.tests.selenium.pages import HomePage

dirname = os.path.dirname(__file__)
driver_path = os.path.join(dirname, '../../../../../../chromedriver')
driver_path = '/Users/marqetintl/Dropbox/MIQ/projects/chromedriver'


class Mixin(TestMixin):
    pass


class TestHomePage(Mixin, LiveServerTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.domain = self.live_server_url

    def test_homepage(self):
        with webdriver.Chrome(driver_path) as driver:  # type: webdriver.Chrome
            page = HomePage(driver).get(self.domain)
            driver.get('http://192.168.1.231:8000/')
            # driver.get(self.domain)
            driver.save_screenshot('screenshot.png')

            print('==>', self.domain)

            # print(driver.page_source)
            # webdriver.wait(driver, 10)
            assert 'This site is currently under construction.' in driver.page_source


# class TestLogin(Mixin, LiveServerTestCase):
#     def setUp(self) -> None:
#         super().setUp()
#         self.domain = self.live_server_url

#     def test_login_success(self):
#         # self.get_user()
#         with webdriver.Chrome(driver_path) as driver:
#             # url = self.domain + self.login_path
#             url = self.domain
#             driver.get(url)
#             # page = LoginPage(driver).get(url)
#             # act_page = page.login(self.username, self.password)

#             # assert 'AccountView' in act_page.driver.page_source
#             # assert 'UserNav' in act_page.driver.page_source
