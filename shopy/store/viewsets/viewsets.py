

from django.contrib.sites.shortcuts import get_current_site
# from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, mixins
# from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import get_object_or_404

from miq.staff.mixins import LoginRequiredMixin

from ..serializers import ShopSettingSerializer
from ..models import ShopSetting


class ShopSettingViewset(
    LoginRequiredMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'slug'
    serializer_class = ShopSettingSerializer
    queryset = ShopSetting.objects.none()
    parser_classes = (JSONParser,)
    permission_classes = (IsAdminUser, )

    def get_object(self):
        return get_object_or_404(ShopSetting, site=get_current_site(self.request))
