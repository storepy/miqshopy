import logging

from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAdminUser

from miq.core.permissions import DjangoModelPermissions

from ..models import Category
from ..serializers import CategorySerializer

from .mixins import ViewSetMixin


log = logging.getLogger(__name__)


class CategoryViewset(ViewSetMixin, viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = (JSONParser, )
    permission_classes = (IsAdminUser, DjangoModelPermissions)

    @action(methods=['patch'], detail=True, url_path=r'publish')
    def publish(self, request, *args, **kwargs):
        obj = self.get_object()
        obj_id = obj.id
        pub = request.data.get('is_published', False)

        log.info(f'Publishing category[{obj_id}]: {pub}')
        if pub:
            required = ['name', 'meta_title', 'meta_slug', ]
            for field in required:
                if not getattr(obj, field, None):
                    log.error(f'Cannot publish category[{obj_id}]: {field} required')
                    raise serializers.ValidationError({field: _('required')})

        obj.is_published = pub
        obj.save()

        return self.retrieve(self, request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().products_count().order_by('-created')

    def perform_create(self, ser):
        name = self.request.data.get('name')
        ser.save(meta_title=name, meta_slug=slugify(name))
