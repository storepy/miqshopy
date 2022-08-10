
from miq.analytics.views import LIBView
from miq.analytics.serializers import LIBSerializer

# from shopy.store.models import Product

from ..serializers import category_to_dict
# from ..serializers import  ProductListSerializer
from ..utils import get_published_categories


class Serializer(LIBSerializer):
    pass


class ShopLIBView(LIBView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        obj = ctx.get('object')
        if not obj:
            return ctx

        data = {
            'lib_data': Serializer(obj).data,
            'categories': [category_to_dict(cat) for cat in get_published_categories()],
        }
        if recent := self.request.session.get('_recent'):
            data['recent'] = recent[:4]
            # data['recent'] = ProductListSerializer(
            #     Product.objects.published().filter(meta_slug__in=recent[:4]), many=True).data

        self.update_sharedData(ctx, data)
        return ctx
