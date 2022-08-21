

from django.contrib.sites.shortcuts import get_current_site
# from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import get_object_or_404

from miq.staff.mixins import LoginRequiredMixin


from ..serializers import ShopSettingSerializer
from ..models import ShopSetting, ShopHit


class RetrieveMixin(LoginRequiredMixin, mixins.RetrieveModelMixin,):
    pass


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


class ShopAnalyticsViewset(RetrieveMixin, viewsets.GenericViewSet):
    lookup_field = 'slug'
    serializer_class = ShopSettingSerializer
    queryset = ShopSetting.objects.none()
    parser_classes = (JSONParser,)
    permission_classes = (IsAdminUser, )

    @action(methods=['GET'], detail=True, url_path=r'notifications')
    def notifications(self, request, *args, **kwargs):
        return Response({})

    @action(methods=['GET'], detail=True, url_path=r'summary')
    def summary(self, request, *args, **kwargs):
        qs = ShopHit.objects.all()
        params = request.query_params

        if range := params.get('__range'):
            if range == 'today':
                qs = qs.today()
            if range == 'week':
                qs = qs.last_7_days()
            if range == 'month':
                qs = qs.last_30_days()

        return Response(get_hit_data(qs=qs))

    def get_object(self):
        return get_object_or_404(ShopSetting, site=get_current_site(self.request))


class ShopSettingViewset(RetrieveMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    lookup_field = 'slug'
    serializer_class = ShopSettingSerializer
    queryset = ShopSetting.objects.none()
    parser_classes = (JSONParser,)
    permission_classes = (IsAdminUser, )

    def get_object(self):
        return get_object_or_404(ShopSetting, site=get_current_site(self.request))
