

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


class ShopStaffIndexView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = {
            'orders': {'count': SupplierOrder.objects.count()},
            'products': {'count': Product.objects.count()},
            'cats': {
                'count': Category.objects.count(),
                'cat_count': list(Product.objects.all().by_category_count())
            },
            'currencies': Currencies,
            'suppliers': SupplierChoices,
            'stages': ProductStages,
        }

        setting = ShopSetting.objects.filter(site=get_current_site(self.request))

        if setting.exists():
            data['shopy_settings'] = ShopSettingSerializer(setting.first()).data

        self.update_sharedData(context, data)

        return context


"""

hits = ShopHit.objects.all()
# .filter(parsed_data__from_source__isnull=False)
external_sources = hits.exclude(parsed_data__from_ref=None)\
    .values('parsed_data__from_ref',)\
    .annotate(count=Count('ip')).order_by('-count')

campaigns = hits.exclude(parsed_data__utm_campaign=None)\
    .values('parsed_data__utm_campaign',)\
    .annotate(count=Count('ip')).order_by('-count')

# 1 being Monday and day 7 being Sunday.
by_week_day = hits\
    .values('created__week_day')\
    .annotate(count=Count('path')).order_by('-count')


ua = hits\
    .values('created__day')\
    .annotate(count=Count('created__day')).order_by('-created')
# .annotate(date=Cast('created__date', output_field=CharField()))\

pprint(list(ua[:10]))


print(hits.count(), ua.count())
"""
