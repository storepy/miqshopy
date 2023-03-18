
from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from miq.core.permissions import DjangoModelPermissions

from ..models import Category
from ..serializers import CategorySerializer
from ..services import category_publish, category_unpublish, category_create, category_delete

from .mixins import ViewSetMixin


class CategoryViewset(ViewSetMixin, viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = (JSONParser, )
    permission_classes = (IsAdminUser, DjangoModelPermissions)

    @action(methods=['patch'], detail=True, url_path=r'publish')
    def publish(self, request, *args, **kwargs):
        if request.data.get('is_published', False) is True:
            category_publish(instance=self.get_object())
        else:
            category_unpublish(instance=self.get_object())

        return self.retrieve(self, request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().products_count().order_by('position', '-created', 'name')

    def perform_create(self, ser: CategorySerializer):
        assert ser.instance is None, 'Instance already exists' + str(ser.instance)
        ser.instance = category_create(**ser.validated_data)

    def perform_destroy(self, instance: Category):
        category_delete(instance=instance)
