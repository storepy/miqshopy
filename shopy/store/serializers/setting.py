# import logging

from re import U
from rest_framework.serializers import ModelSerializer, JSONField

from ..models import ShopSetting


class ShopSettingPagesSerializer(ModelSerializer):
    class Meta:
        model = ShopSetting
        read_only_fields = ('slug',)
        fields = (
            'returns', 'returns_html', 'size_guide', 'size_guide_html',
            *read_only_fields
        )


class ShopSettingSerializer(ModelSerializer):
    class Meta:
        model = ShopSetting
        read_only_fields = ('slug', 'currencies', 'suppliers')
        fields = (
            'currency', 'config', *ShopSettingPagesSerializer.Meta.fields,
            *read_only_fields)

    currencies = JSONField(read_only=True)
    suppliers = JSONField(read_only=True)
