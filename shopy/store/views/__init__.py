

# from django.db.models.functions import Cast
# from django.db.models import Count, CharField
# import requests
# from pprint import pprint
from miq.analytics.models import Bot
# from miq.analytics.models import  Hit
from django.db import models
from ..models import ProductHit
from django.contrib.sites.shortcuts import get_current_site
# from django.http import JsonResponse

# from rest_framework import serializers
# from rest_framework.response import Response
# from rest_framework.decorators import api_view


from miq.staff.views import IndexView
from miq.core.models import Currencies

# from miq.analytics.models import Hit
# from miq.analytics.serializers import HitSerializer

from ..serializers import ShopSettingSerializer, get_product_serializer_class, get_category_serializer_class
from ..models import Product, Category, SupplierOrder, ShopSetting, SupplierChoices, ProductStages

from .v_product import StaffProductsView, StaffProductView
from .v_category import StaffCategoryView

__all__ = (
    'ShopStaffIndexView',
    'StaffProductsView', 'StaffProductView',
    'StaffCategoryView'
)


def get_base_context_data(request):
    data = {'currencies': Currencies, 'suppliers': SupplierChoices, 'stages': ProductStages}

    if (setting := ShopSetting.objects.filter(site=get_current_site(request))) and setting.exists():
        data['shopy_settings'] = ShopSettingSerializer(setting.first()).data
    return data


CategoryListSerializer = get_category_serializer_class(extra_read_only_fields=('name', 'cover_data'))
ProductListSerializer = get_product_serializer_class(extra_read_only_fields=('name', 'cover_data', 'url'))


class ShopStaffIndexView(IndexView):
    qs = ProductHit.objects.exclude(ip__in=Bot.objects.values_list('ip', flat=True))

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
            'stats': self.get_stats(),

        }

        self.get_store_issues(data)

        self.update_sharedData(context, data)

        return context

    def get_stats(self):
        data = {
            'msg_count': self.qs.filter(url__icontains='r=1').values('ip', 'url').annotate(c=models.Count('url')).count(),
            'views_count': self.qs.values('url').annotate(c=models.Count('url')).count(),
            'visitor_count': self.qs.values('ip').annotate(c=models.Count('ip')).count(),
        }

        data['prods'] = [
            {**ProductListSerializer(Product.objects.get(pk=p.get('product__pk'))).data, 'count': p.get('count')} for p in
            self.qs.values('product__pk').annotate(count=models.Count('product__pk')).order_by('-count')[:10]
        ]
        data['cats'] = [
            {**CategoryListSerializer(Category.objects.get(pk=p.get('product__category__pk'))).data, 'count': p.get('count')} for p in
            self.qs.values('product__category__pk')
            .annotate(count=models.Count('product__category__pk'))
            .order_by('-count')[:10]
        ]

        return data

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


# qs = Hit.objects.all()
# # qs = qs.filter(parsed_data__from_ref__icontains='facebook.com')
# qs = qs.filter(parsed_data__from_ref__isnull=False)
# qs = qs.values('parsed_data__from_ref').annotate(c=models.Count('parsed_data__from_ref')).order_by('-c')

# # pprint(list(qs[:16]))


# v = ProductHit.objects.first()
# v = Bot.objects.all()[11]
# ip = v.ip

# # r = requests.get(f'https://ipapi.co/{ip}/json/').json()

# print(ip)
# # pprint(r)
