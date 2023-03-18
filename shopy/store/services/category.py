import logging

from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ..models import Category


log = logging.getLogger(__name__)


def category_publish(*, instance: Category) -> None:
    pk = instance.id

    required = ['name', 'meta_title', 'meta_slug']
    for field in required:
        if getattr(instance, field, None):
            continue

        log.error(f'[{pk}]: Category field "{field}" required')
        raise serializers.ValidationError({field: _('required')})

    instance.publish()
    log.info(f'[{pk}]: Category published')


def category_unpublish(*, instance: Category) -> None:
    instance.unpublish()
    log.info(f'[{instance.id}]: Category unpublished')


def category_create(**kwargs: dict) -> Category:
    name = kwargs.get('name')
    meta_title = kwargs.get('meta_title', name)
    meta_slug = kwargs.get('meta_slug', name)

    c = Category(
        **kwargs, meta_title=meta_title, meta_slug=slugify(meta_slug),
        position=Category.objects.count() + 1
    )

    c.full_clean()
    c.save()

    log.info(f'[{c.pk}]: Category added')

    return c


def category_list_parent_qs(*, filters: dict = None) -> list[Category]:
    qs = Category.objects.filter(parent__isnull=True)
    if not filters:
        return qs

    return qs


def category_list_qs(*, filters: dict = None) -> list[Category]:
    qs = Category.objects.all()
    if not filters:
        return qs

    return qs


def category_delete(*, instance: Category) -> None:
    pk = instance.id

    instance.delete()

    if page := instance.page:
        page.delete()

    if cover := instance.cover:
        cover.delete()

    log.info(f'[{pk}]: Category deleted')
