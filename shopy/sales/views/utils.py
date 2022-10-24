
from django.contrib.sites.shortcuts import get_current_site

from ...store.serializers import ShopSettingSerializer
from ...store.models import ShopSetting


def get_sales_view_base_context_data(request):
    data = {}

    if (setting := ShopSetting.objects.filter(site=get_current_site(request))) and setting.exists():
        data['shopy_settings'] = ShopSettingSerializer(setting.first()).data

    return data
