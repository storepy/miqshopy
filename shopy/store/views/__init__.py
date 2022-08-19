

from django.contrib.sites.shortcuts import get_current_site
# from django.http import JsonResponse

# from rest_framework import serializers

from miq.staff.views import IndexView
from miq.core.models import Currencies

# from miq.analytics.models import Hit
# from miq.analytics.serializers import HitSerializer

from ..serializers import ShopSettingSerializer
from ..models import ShopHit
from ..models import Product, Category, SupplierOrder, ShopSetting, SupplierChoices, ProductStages


def get_hit_data(*, qs=ShopHit.objects.all()):
    hits = ShopHit.objects.order_by('-created')

    def serialize(qs, t):
        assert t is not None
        items = []
        for i in qs.all():
            i = dict(i)
            item = hits.filter(path=i['path']).order_by('-created').first()
            if item and (_data := item.session_data):
                i['name'] = _data.get('name')
                i['img'] = _data.get('img')
            items.append(i)
        return items

    return {
        # uniques
        'views_count': qs.paths_by_ips().count(),
        'visitors_count': qs.by_ips().count(),
        'sent_message': qs.sent_message().paths_by_ips().count(),
        'top_products': serialize(qs.filter(model='product').by_paths()[:10], 'product'),
        'top_cats': serialize(qs.filter(model='category').by_paths()[:10], 'category')
    }


class ShopStaffIndexView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = {
            'hits': get_hit_data(qs=ShopHit.objects.all()),
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
