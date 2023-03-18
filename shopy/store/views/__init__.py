from django.db import models
from django.contrib.sites.shortcuts import get_current_site

from miq.analytics.models import Bot
from miq.staff.views import IndexView
from miq.core.models import Currencies


from ..models import ProductHit
from ..models import Product, Category, SupplierOrder, ShopSetting, SupplierChoices, ProductStages
from ..serializers import ShopSettingSerializer, get_product_serializer_class, get_category_serializer_class

from .v_product import StaffProductsView, StaffProductView,StaffProductCreateView
from .v_category import StaffCategoryView

__all__ = (
    'ShopStaffIndexView',
    'StaffProductsView', 'StaffProductView',
    'StaffCategoryView'
)


def get_base_context_data(request):
    data = {'currencies': Currencies, 'suppliers': SupplierChoices, 'stages': ProductStages}

    if (setting := ShopSetting.objects.filter(site=get_current_site(request))) and setting.exists():
        data['shopy_settings'] = ShopSettingSerializer(setting.first()).data
    return data


CategoryListSerializer = get_category_serializer_class(extra_read_only_fields=('name', 'cover_data'))
ProductListSerializer = get_product_serializer_class(extra_read_only_fields=('name', 'cover_data', 'url'))


class ShopStaffIndexView(IndexView):
    qs = ProductHit.objects.exclude(ip__in=Bot.objects.values_list('ip', flat=True))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = {
            **get_base_context_data(self.request),
            'orders': {'count': SupplierOrder.objects.count()},
            'products': {'count': Product.objects.count()},
            'cats': {
                'count': Category.objects.count(),
                'cat_count': list(Product.objects.all().by_category_count())
            },
            'stats': self.get_stats(),

        }

        self.get_store_issues(data)

        self.update_sharedData(context, data)

        return context

    def get_stats(self):
        data = {
            'msg_count': self.qs.filter(url__icontains='r=1').values('ip', 'url').annotate(c=models.Count('url')).count(),
            'views_count': self.qs.values('url').annotate(c=models.Count('url')).count(),
            'visitor_count': self.qs.values('ip').annotate(c=models.Count('ip')).count(),
        }

        data['prods'] = [
            {**ProductListSerializer(Product.objects.get(pk=p.get('product__pk'))).data, 'count': p.get('count')} for p in
            self.qs.values('product__pk').annotate(count=models.Count('product__pk')).order_by('-count')[:10]
        ]
        data['cats'] = [
            {**CategoryListSerializer(Category.objects.get(pk=p.get('product__category__pk'))).data, 'count': p.get('count')} for p in
            self.qs.values('product__category__pk')
            .annotate(count=models.Count('product__category__pk'))
            .order_by('-count')[:10]
        ]

        return data

    def get_store_issues(self, data):
        assert isinstance(data, dict)

        _qs = Product.objects.published()
        has_issues = False
        issues = {}

        if (qs := _qs.has_no_description()) and qs.exists():
            has_issues = True
            issues['no_des'] = qs.count()

        if (qs := _qs.has_name_gt_65()) and qs.exists():
            has_issues = True
            issues['name_gt_65'] = qs.count()

        if (qs := _qs.has_meta_slug_gt_100()) and qs.exists():
            has_issues = True
            issues['meta_slug_gt_100'] = qs.count()

        if (qs := _qs.has_no_sizes()) and qs.exists():
            has_issues = True
            issues['no_size'] = qs.count()

        if has_issues:
            data['issues'] = issues
            data['has_issues'] = has_issues
