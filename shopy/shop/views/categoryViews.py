from django.shortcuts import get_object_or_404

from miq.core.views.generic import ListView
from miq.core.serializers import serialize_context_pagination

from ...store.models import Product, Category
from ...sales.api import APIProductListSerializer

from .mixins import ViewMixin


class CategoryView(ViewMixin, ListView):
    model = Product
    category = None  # type: 'Category'
    template_name = 'shop/products.django.html'

    def get_context_data(self, **kwargs) -> dict:
        ctx = super().get_context_data(**kwargs)

        # SEO
        ctx['object'] = self.category
        ctx['title'] = self.category.meta_title
        ctx['meta_description'] = self.category.meta_description

        # sD
        data = {
            'page_label': self.category.name,
            'breadcrumbs': [
                {'label': 'Accueil', 'path': '/'},
                {'label': 'Catalogue', 'path': '/shop/'},
            ],
            'object_list': APIProductListSerializer(ctx.get('object_list'), many=True).data,
            'pagination': serialize_context_pagination(self.request, ctx)
        }
        self.update_sharedData(ctx, data)

        return ctx

    def get_queryset(self):
        return self.category.get_products().published().order_for_shop()
        # return self.category.products.published().order_for_shop()

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category.objects.published().has_products(),
            meta_slug=self.kwargs.get('category_meta_slug')
        )
        return super().dispatch(request, *args, **kwargs)
