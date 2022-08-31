import datetime

from django.db import models
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAdminUser

from miq.staff.mixins import LoginRequiredMixin
from miq.analytics.serializers import HitSerializer
from miq.analytics.viewsets import get_hit_qs

from ..models import ShopHit


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
        'top_cats': serialize(qs.filter(model='category').by_paths()[:10], 'category')
    }


class StoreInsightsViewset(LoginRequiredMixin, viewsets.GenericViewSet):
    lookup_field = 'slug'
    queryset = ShopHit.objects.none()
    parser_classes = (JSONParser,)
    permission_classes = (IsAdminUser, )

    @action(methods=['GET'], detail=True,)
    def products(self, request, *args, **kwargs):
        qs = ShopHit.objects.products()
        params = request.query_params
        day = None
        limit = None

        if window := params.get('__window'):
            day = timezone.now()
            if window == 'today':
                qs = qs.today()
                limit = models.Q(created__date=day)
            if window == 'yst':
                qs = qs.yesterday()
                day = day - datetime.timedelta(days=1)
                limit = models.Q(created__date=day)

            if window == 'last_7':
                qs = qs.last_7_days()
            if window == 'last_14':
                qs = qs.last_14_days()
            if window == 'last_30':
                qs = qs.last_30_days()

            if day and not limit:
                limit = models.Q(created__date__gte=day)
            # return self.filter(created__gte=day).order_by('-created')

        qs = qs.values('path')\
            .annotate(
                msg_count=models.Count('parsed_data__r', filter=limit),
                ip_count=models.Count('ip', distinct=True, filter=limit),
                id_count=models.Count('id', distinct=True),
                x_count=models.Count('parsed_data__from_ref',)
                # This would group by external source: so ig would count for 1 for ex
                # x_count=models.Count('parsed_data__from_ref', distinct=True)
        ).order_by('-msg_count', '-x_count', '-ip_count', '-id_count')
        return self._paginate(qs)

    @action(methods=['GET'], detail=True,)
    def categories(self, request, *args, **kwargs):
        qs = ShopHit.objects.categories().values('path')\
            .annotate(
                ip_count=models.Count('ip', distinct=True),
                id_count=models.Count('id', distinct=True),
                x_count=models.Count('parsed_data__from_ref', )
        ).order_by('-ip_count')
        return self._paginate(qs)

    @action(methods=['GET'], detail=True, url_path=r'hits')
    def hits(self, request, *args, **kwargs):
        qs = get_hit_qs(request, qs=ShopHit.objects.filter(model='product'))
        queryset = self.filter_queryset(qs)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = HitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = HitSerializer(queryset, many=True)
        return Response(serializer.data)

    def _paginate(self, queryset):
        qs = self.filter_queryset(queryset)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(qs)
