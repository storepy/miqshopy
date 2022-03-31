from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse

from rest_framework import serializers

from miq.staff.views import IndexView
from miq.core.models import Currencies
from miq.core.views.generic import ListView


from ..serializers import ShopSettingSerializer, SupplierItemSerializer
from ..models import Product, Category, SupplierOrder, ShopSetting, SupplierChoices, ProductStages
from ..models import SupplierItem


class ShopStaffIndexView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = {
            'orders': {'count': SupplierOrder.objects.count()},
            'products': {'count': Product.objects.count()},
            'cats': {'count': Category.objects.count()},
            'currencies': Currencies,
            'suppliers': SupplierChoices,
            'stages': ProductStages
        }

        setting = ShopSetting.objects.filter(site=get_current_site(self.request))
        if setting.exists():
            data['shopy_settings'] = ShopSettingSerializer(setting.first()).data

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
        print(data)
        return JsonResponse(data)
