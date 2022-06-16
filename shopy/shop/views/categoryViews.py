from django.shortcuts import get_object_or_404

from miq.core.views.generic import ListView
from miq.core.serializers import serialize_context_pagination
from shopy.store.models import Product, Category

from ..serializers import ProductListSerializer
from .mixins import ViewMixin


class CategoryView(ViewMixin, ListView):
    model = Product
    category = None  # type: 'Category'
    template_name = 'shop/products.django.html'

    def get_context_data(self, **kwargs) -> dict:
        ctx = super().get_context_data(**kwargs)

        # SEO
        ctx['title'] = self.category.meta_title
        ctx['meta_description'] = self.category.meta_description

        # sD
        data = {
            'object_list': ProductListSerializer(ctx.get('object_list'), many=True).data,
            'pagination': serialize_context_pagination(self.request, ctx)
        }
        data.update({
            'page_label': self.category.name,
            'breadcrumbs': [
                {'label': 'Accueil', 'path': '/'},
                {'label': 'Catalogue', 'path': '/shop/'},
            ],
        })
        self.update_sharedData(ctx, data)

        return ctx

    def get_queryset(self):
        sp = self.kwargs.get('category_meta_slug')
        self.category = get_object_or_404(
            Category.objects.published().has_products(),
            meta_slug=sp)
        return self.category.products.published()\
            .order_by('is_oos', 'stage', 'position', '-created', 'name')
