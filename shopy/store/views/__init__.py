

from django.db import models
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse

from rest_framework import serializers

from miq.staff.views import IndexView
from miq.core.models import Currencies
from miq.core.views.generic import ListView

from miq.analytics.models import Hit
from miq.analytics.serializers import HitSerializer


from ..serializers import ShopSettingSerializer, SupplierItemSerializer
from ..models import Product, Category, SupplierOrder, ShopSetting, SupplierChoices, ProductStages
from ..models import SupplierItem


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

        hits = Hit.public.filter(path__icontains='/shop')\
            .exclude(path='/shop/')\
            .key_by_created_date('session')

        # data['hits'] = HitSerializer(hits[:100], many=True).data
        data['hits'] = [*hits[:100]]

        self.update_sharedData(context, data)

        return context


class TrackItemSerializer(SupplierItemSerializer):
    class Meta(SupplierItemSerializer.Meta):
        read_only_fields = ('slug', 'supplier', 'url')
        fields = ('cost', *read_only_fields)

    supplier = serializers.CharField(read_only=True)


class TrackrListView(ListView):
    queryset = SupplierItem.objects.order_by('-created').prefetch_related('order')\
        .filter(slug='f332f1ff-02c1-484c-a450-6d8ece698458')
    paginate_by = 100

    def get(self, request, *args, **kwargs):
        r = super().get(request, *args, **kwargs)
        ctx = r.context_data
        qs = ctx.get('object_list')
        data = {
            'qs': TrackItemSerializer(qs, many=True).data
        }
        return JsonResponse(data)


class Path:
    def __init__(self, qs, *args, **kwargs):
        from pprint import pprint
        print(' == PATH ==')
        self.qs = qs
        wha = qs.filter(response_status=302)
        # print('wha', wha.values('pk', 'ip'))
        wha_ips = wha.values('ip').annotate(ip_count=models.Count('ip'))
        pprint(wha.values('ip').distinct())
        pprint(wha_ips)

        hits = qs.filter(ip__in=wha_ips.values_list('ip', flat=True))
        print(hits.count())
        # pprint([p for p in self.sessions_by_path()])

        # hits = qs.values('referrer').annotate(path_count=models.Count('path')).order_by('-path_count')

        paths = qs.values('path').annotate(path_count=models.Count('path'))
        print(paths.count())
        s = paths.annotate(session_count=models.Count('session'))

        # pprint([p for p in s])

    # def top_referrings(self, count=10) -> list:
    #     return Counter(self.referrings.values_list('path', flat=True))\
    #         .most_common(count)

    # def top_referrers(self, count=10) -> list:
    #     return Counter(self.referrers.values_list('referrer', flat=True))\
    #         .most_common(count)

    def sessions_by_path(self):
        return self.qs.values('path').annotate(session_count=models.Count('session'))
