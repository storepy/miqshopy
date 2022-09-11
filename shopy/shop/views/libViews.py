
from miq.analytics.views import LIBView
from miq.analytics.serializers import LIBSerializer

from ..serializers import category_to_dict
from ..utils import get_published_categories


class ShopLIBView(LIBView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        obj = ctx.get('object')
        if not obj:
            return ctx

        data = {
            'lib_data': LIBSerializer(obj).data,
            'categories': [category_to_dict(cat) for cat in get_published_categories()],
        }
        if recent := self.request.session.get('_recent'):
            data['recent'] = recent[:4]

        self.update_sharedData(ctx, data)
        return ctx
