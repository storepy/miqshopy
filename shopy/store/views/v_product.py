

from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site


from miq.core.models import Currencies
from miq.core.serializers import serialize_context_pagination
from miq.staff.views.generic import ListView

from ..viewsets.product import get_product_qs
from ..utils import get_category_options, get_product_size_choices
from ..serializers import ShopSettingSerializer, ProductSerializer, ProductListSerializer
from ..models import Product, ShopSetting, SupplierChoices, ProductStages


def get_base_context_data(request):
    data = {
        'currencies': Currencies, 'suppliers': SupplierChoices, 'stages': ProductStages,
        # TODO: cache categories
        'categories': get_category_options(),
        'sizes': get_product_size_choices(),
    }

    if (setting := ShopSetting.objects.filter(site=get_current_site(request))) and setting.exists():
        data['shopy_settings'] = ShopSettingSerializer(setting.first()).data
    return data


# class StaffProductView(MultipleObjectMixin, DetailView):
class StaffProductView(ListView):
    model = Product
    template_name = 'store/base.django.html'
    slug_field = 'slug'
    paginate_by = 20

    def get_queryset(self):
        qs = get_product_qs(self.request, qs=super().get_queryset(), params=self.request.GET)

        self.object = get_object_or_404(qs, slug=self.kwargs.get('slug'))
        return qs
    # slug_url_kwarg = 'product_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = {
            **get_base_context_data(self.request),
            'product': ProductSerializer(self.object).data,
            'products': ProductListSerializer(context.get('object_list'), many=True).data,
            'pagination': serialize_context_pagination(self.request, context)
        }

        self.update_sharedData(context, data)

        return context


class StaffProductsView(ListView):
    model = Product
    template_name = 'store/base.django.html'
    paginate_by = 20

    def get_queryset(self):
        return get_product_qs(self.request, qs=super().get_queryset(), params=self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'Products - Store'

        data = {
            **get_base_context_data(self.request),
            'products': ProductListSerializer(context.get('object_list'), many=True).data,
            'pagination': serialize_context_pagination(self.request, context)
        }

        self.update_sharedData(context, data)

        return context
