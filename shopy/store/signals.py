import uuid
from django.dispatch import receiver
from django.db.models import signals
from django.contrib.sites.models import Site

from .viewsets.product import local

from .models import Product, Category, ShopSetting, ProductPage, CategoryPage, ProductImage


def create_page(instance, PageModel):
    site = getattr(local, 'site', Site.objects.get_current())
    return PageModel.objects.create(
        site=site, title=instance.meta_title,
        meta_slug=instance.meta_slug or uuid.uuid4()
    )


def update_page(instance, page):
    page.title = instance.meta_title
    page.meta_slug = instance.meta_slug or uuid.uuid4()
    return page


@receiver(signals.pre_save, sender=Product)
def on_product_will_save(sender, instance, **kwargs):
    if not instance.pk:
        page = ProductPage.objects.filter(meta_slug=instance.meta_slug).first()
        if not page:
            page = create_page(instance, ProductPage)

        instance.page = page
        return

    name = instance.name
    if((old := sender.objects.get(pk=instance.pk)) and old.name != name):
        if instance.cover:
            instance.cover.alt_text = name
            instance.cover.save()

        if (img_qs := instance.images) and img_qs.exists():
            img_qs.update_alt_texts(name, with_position=True)


@receiver(signals.post_save, sender=Product)
def on_product_did_save(sender, instance, **kwargs):
    page = update_page(instance, instance.page)
    page.save()


@receiver(signals.pre_delete, sender=Product)
def on_product_will_be_deleted(sender, instance, **kwargs):
    if cover := instance.cover:
        # proxy issue
        ProductImage.objects.get(id=cover.id).delete()

    if (attrs := instance.attributes) and attrs.exists():
        attrs.all().delete()

    if (imgs := instance.images) and imgs.exists():
        imgs.all().delete()


@receiver(signals.post_delete, sender=Product)
def on_product_was_deleted(sender, instance, ** kwargs):
    # protect: cannot delete a product with a page
    if page := instance.page:
        page.delete()


@receiver(signals.pre_save, sender=Category)
def on_category_will_save(sender, instance, **kwargs):
    if not instance.pk:
        instance.page = create_page(instance, CategoryPage)
        return


@receiver(signals.post_save, sender=Category)
def on_category_did_save(sender, instance, **kwargs):
    page = update_page(instance, instance.page)
    page.save()


@receiver(signals.post_delete, sender=Category)
def on_category_was_deleted(sender, instance, **kwargs):
    if page := instance.page:
        page.delete()

    if cover := instance.cover:
        cover.delete()


@receiver(signals.post_save, sender=Site)
def on_site_did_save(sender, instance, created, **kwargs):
    if not ShopSetting.objects.filter(site=instance).exists():
        ShopSetting.objects.create(site=instance)
