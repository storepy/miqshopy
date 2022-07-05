from django.contrib.sites.shortcuts import get_current_site

from miq.core.models import Index
from miq.core.views.generic import TemplateView

from shopy.store.models import Product
from ..utils import get_published_categories


class IndexView(TemplateView):
    template_name = 'shop/index.django.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        site = get_current_site(self.request)
        page = Index.objects.filter(site=site).first()
        if not page:
            return ctx

        ctx['page'] = page
        ctx['sections'] = page.sections.exclude(html='')
        ctx['title'] = page.title

        if new_products := Product.objects.published().is_new().slice(count=4):
            ctx['new_products'] = new_products

        if sale_products := Product.objects.published()\
                .is_on_sale().slice(count=4):
            ctx['sale_products'] = sale_products

        if categories := get_published_categories():
            ctx['categories'] = categories

        # ctx['occasions'] = Category.objects.published()\
        # .order_by('created')[:10]

        return ctx
