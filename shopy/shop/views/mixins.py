
from miq.core.utils import get_session


class ViewMixin:

    def get_session(self):
        return get_session(self.request)

    # def object_list_pagination_to_dict(self, __context: dict) -> dict:
    #     return {
    #         'object_list': ProductListSerializer(__context.get('object_list'), many=True).data,
    #         'pagination': serialize_context_pagination(self.request, __context)
    #     }
