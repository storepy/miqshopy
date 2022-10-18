from django.apps import apps
from django.db.models import Q
from django.core.management.base import BaseCommand

from ...models import Product, Category, ShopHit


def get_hits():
    return ShopHit.objects.filter(
        Q(model__isnull=True)
        | Q(app__isnull=True)
    ).distinct()


class Command(BaseCommand):
    help = 'Add app and model to shop hits'

    def handle(self, *args, **kwargs):
        if not apps.is_installed('miq.analytics'):
            print('Analytics app not installed')
            return

        print('Updating', get_hits().count(), 'hits ...')

        for item in Product.objects.exclude(meta_slug__isnull=True):
            hits = get_hits().filter(path__icontains=item.meta_slug)
            if not hits.exists():
                continue

            session_data = item.get_hit_data() or {}
            session_data.pop('app', None)
            session_data.pop('model', None)

            hits.update(app=item._meta.app_label, model=item._meta.model_name)

            for hit in hits.filter(session_data__name__isnull=True):
                print(hit.session_data)

        for item in Category.objects.exclude(meta_slug__isnull=True):
            hits = get_hits().filter(path__icontains=item.meta_slug)
            if not hits.exists():
                continue

            hits.update(app=item._meta.app_label, model=item._meta.model_name)

        remaining = get_hits().exclude(path='/shop/')
        print('Remainin', remaining.count())
        print(remaining)
