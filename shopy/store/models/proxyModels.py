from miq.core.models import Page, Image


class ProductImage(Image):
    class Meta:
        proxy = True


class ProductPage(Page):
    class Meta:
        proxy = True

    # objects = ProductPageManager()

    def save(self, *args, **kwargs):
        self.source = 'shopy_product'
        super().save(*args, **kwargs)


class CategoryPage(Page):
    class Meta:
        proxy = True

    # objects = ProductCategoryPageManager()

    def save(self, *args, **kwargs):
        self.source = 'shopy_category'
        super().save(*args, **kwargs)
