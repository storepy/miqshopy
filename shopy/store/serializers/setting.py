# import logging

from rest_framework.serializers import ModelSerializer, JSONField

from ..models import ShopSetting


class ShopSettingSerializer(ModelSerializer):
    class Meta:
        model = ShopSetting
        read_only_fields = ('slug', 'currencies', 'suppliers')
        fields = ('currency', 'config', *read_only_fields)

    currencies = JSONField(read_only=True)
    suppliers = JSONField(read_only=True)
