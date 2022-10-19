

# from django.db.models.functions import Cast
# from django.db.models import Count, CharField
# from pprint import pprint
from django.contrib.sites.shortcuts import get_current_site
# from django.http import JsonResponse

# from rest_framework import serializers
# from rest_framework.response import Response
# from rest_framework.decorators import api_view


from miq.staff.views import IndexView
from miq.core.models import Currencies

# from miq.analytics.models import Hit
# from miq.analytics.serializers import HitSerializer

from ..serializers import ShopSettingSerializer
from ..models import Product, Category, SupplierOrder, ShopSetting, SupplierChoices, ProductStages

from .v_product import StaffProductsView, StaffProductView

__all__ = (
    'ShopStaffIndexView',
    'StaffProductsView', 'StaffProductView'
)


def get_base_context_data(request):
    data = {'currencies': Currencies, 'suppliers': SupplierChoices, 'stages': ProductStages}

    if (setting := ShopSetting.objects.filter(site=get_current_site(request))) and setting.exists():
        data['shopy_settings'] = ShopSettingSerializer(setting.first()).data
    return data


class ShopStaffIndexView(IndexView):
    def get_store_issues(self, data):
        assert isinstance(data, dict)

        _qs = Product.objects.published()
        has_issues = False
        issues = {}

        if (qs := _qs.has_no_description()) and qs.exists():
            has_issues = True
            issues['no_des'] = qs.count()

        if (qs := _qs.has_name_gt_65()) and qs.exists():
            has_issues = True
            issues['name_gt_65'] = qs.count()

        if (qs := _qs.has_meta_slug_gt_100()) and qs.exists():
            has_issues = True
            issues['meta_slug_gt_100'] = qs.count()

        if (qs := _qs.has_no_sizes()) and qs.exists():
            has_issues = True
            issues['no_size'] = qs.count()

        if has_issues:
            data['issues'] = issues
            data['has_issues'] = has_issues

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = {
            **get_base_context_data(self.request),
            'orders': {'count': SupplierOrder.objects.count()},
            'products': {'count': Product.objects.count()},
            'cats': {
                'count': Category.objects.count(),
                'cat_count': list(Product.objects.all().by_category_count())
            },

        }

        self.get_store_issues(data)

        self.update_sharedData(context, data)

        return context
