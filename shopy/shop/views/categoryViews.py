import typing
from django.shortcuts import get_object_or_404

from miq.core.views.generic import ListView
from miq.core.serializers import serialize_context_pagination

from ...store.models import Product, Category
from ...sales.api import APIProductListSerializer

from ..services import (
    product_qs, ProductFilterSerializer,
    category_qs, category_hit_create,
    customer_get_from_request
)

from .mixins import ViewMixin


class CategoryView(ViewMixin, ListView):
    model: typing.Type[Product] = Product
    category: Category = None
    paginate_by: int = 12
    template_name: typing.Literal = 'shop/products.django.html'

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
        filters = ProductFilterSerializer(data=self.request.GET)
        if filters.is_valid():
            return product_qs(filters=filters.validated_data).filter(category=self.category).order_for_shop()

        return self.model.objects.none()

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(category_qs(), meta_slug=self.kwargs.get('category_meta_slug'))

        res = super().dispatch(request, *args, **kwargs)

        try:
            category_hit_create(
                category=self.category, request=request, response=res,
                customer=customer_get_from_request(request, response=res),
            )
        except Exception:
            pass

        return res
