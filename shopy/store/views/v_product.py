

from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site


from miq.core.models import Currencies
from miq.core.serializers import serialize_context_pagination
from miq.staff.views.generic import ListView

from ..services import product_list_qs, ProductListFilterSerializer
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


class StaffProductView(ListView):
    model = Product
    template_name = 'store/base.django.html'
    slug_field = 'slug'
    paginate_by = 20

    def get_queryset(self):
        filters = ProductListFilterSerializer(data=self.request.GET)

        qs = Product.objects.none()

        # try catch
        try:
            filters.is_valid(raise_exception=True)
        except Exception as e:
            print(e)
        else:
            qs = product_list_qs(filters=filters.validated_data)

        self.object = get_object_or_404(qs, slug=self.kwargs.get('slug'))

        return qs.order_by('position', '-created', 'name')

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
    paginate_by = 20
    template_name = 'store/base.django.html'

    def get_queryset(self):
        filters = ProductListFilterSerializer(data=self.request.GET)

        # try catch
        filters.is_valid(raise_exception=True)

        return product_list_qs(filters=filters.validated_data).order_by('position', '-created', 'name')

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
