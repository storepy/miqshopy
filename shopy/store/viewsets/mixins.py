
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site

from miq.staff.mixins import LoginRequiredMixin

from ..models import Category, ShopSetting


class ViewSetMixin(LoginRequiredMixin):
    def get_category_options(self) -> dict:
        cats = Category.objects.all()
        return {
            'count': cats.count(),
            'items': [
                {
                    'label': cat.name,
                    'slug': cat.slug,
                    'value': cat.slug
                } for cat in cats
            ]
        }

    def get_setting(self):
        return ShopSetting.objects.filter(site=get_current_site(self.request)).first()
