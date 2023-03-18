
# from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site

from miq.staff.views.generic import DetailView
# from miq.core.serializers import serialize_context_pagination

from ..utils import get_category_options
from ..serializers import ShopSettingSerializer, CategorySerializer
from ..models import Category, ShopSetting


def get_base_context_data(request):
    data = {}

    if (setting := ShopSetting.objects.filter(site=get_current_site(request))) and setting.exists():
        data['shopy_settings'] = ShopSettingSerializer(setting.first()).data
    return data


class StaffCategoryView(DetailView):
    model = Category
    slug_field = 'slug'
    template_name = 'store/base.django.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = {
            **get_base_context_data(self.request),
            'category': CategorySerializer(self.object).data,
            'top_categories': get_category_options(top=True, exclude=[self.object.slug])
        }

        self.update_sharedData(context, data)

        return context
