import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..models import SupplierOrder


log = logging.getLogger(__name__)


def supplier_order_mark_paid(*, instance: SupplierOrder) -> None:
    instance.mark_paid()
    log.info(f'[{instance.pk}]: Supplier order marked as paid')


def supplier_order_create(**kwargs: dict) -> SupplierOrder:
    instance = SupplierOrder(**kwargs)

    instance.full_clean()
    instance.save()

    log.info(f'[{instance.pk}]: Supplier order added')
    return instance


def supplier_order_qs(*, filters: dict = None) -> models.QuerySet:
    qs = SupplierOrder.objects.all()
    if not filters:
        return qs

    return qs


def supplier_order_delete(*, instance: SupplierOrder) -> None:
    pk = instance.id

    instance.delete()
    log.info(f'[{pk}]: Supplier order deleted')
