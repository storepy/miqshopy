
from decimal import Decimal
from urllib.parse import urlencode

from django.db import models
from django.utils import timezone
from django.urls import reverse_lazy
from django.utils.text import capfirst
# from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin
from miq.core.utils import get_text_choices, truncate_str

# from miq.core.middleware import local

from .supplierModels import SupplierChoice
from .managers import ProductManager

app_name = 'store'


class ProductStage(models.TextChoices):
    A_VIRTUAL = 'A_VIRTUAL', _('Virtual stock')  # just added to shop
    B_SUPPLIER_TRANSIT = 'B_SUPPLIER_TRANSIT', _('Ordered from supplier')
    C_INSTORE_WAREHOUSE = 'C_INSTORE_WAREHOUSE', _('Received from supplier')
    D_INSTORE_TRANSIT = 'D_INSTORE_TRANSIT', _('In transit to store')
    E_INSTORE = 'E_INSTORE', _('Available for purchase')
    F_SOLDOUT = 'F_SOLDOUT', _('Sold Out')


ProductStages = get_text_choices(ProductStage)

# gender: female, male, unisex.


class Product(BaseModelMixin):

    category = models.ForeignKey(
        f'{app_name}.Category', related_name='products',
        null=True, blank=True,
        on_delete=models.PROTECT)

    """
    PAGE
    """

    page = models.OneToOneField(
        f'{app_name}.ProductPage', on_delete=models.PROTECT,
        blank=True, null=True, related_name='shopy_product')

    """
    PRICING
    """

    retail_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.01'))])

    is_pre_sale = models.BooleanField(
        _("Available for pre sale"), default=False)
    is_pre_sale_text = models.TextField(
        _("Pre sale description"), null=True, blank=True)
    is_pre_sale_dt = models.DateTimeField(
        _("Availability date time"), blank=True, null=True)

    #
    # is_available = models.BooleanField(_("Is on sale"), default=False)
    is_on_sale = models.BooleanField(_("Is on sale"), default=False)
    is_oos = models.BooleanField(_("Is out of stock"), default=False)
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)])
    is_explicit = models.BooleanField(
        _("Exclude from facebook commerce feed"),
        default=False
    )

    """
    DETAILS
    """

    name = models.CharField(_("Name"), max_length=200, help_text="Recommend 99")
    description = models.TextField(_("Description"), null=True, blank=True)

    """
    IMAGES
    """

    cover = models.OneToOneField(
        f'{app_name}.ProductImage',
        verbose_name=_("Cover"), on_delete=models.SET_NULL, blank=True, null=True
    )

    # TODO: Limit to 10
    images = models.ManyToManyField(
        f'{app_name}.ProductImage', blank=True,
        related_name='shopy_products'
    )

    """
    CONFIG
    """

    # used to alter product collections order, along side position
    is_pinned = models.BooleanField(_("Is pinned"), default=False)

    # use to group similar items with different colors
    color_group_pk = models.CharField(
        _("Color group identifier"), max_length=99,
        null=True, blank=True
    )
    supplier = models.CharField(
        verbose_name=_('Supplier'),
        max_length=50, choices=SupplierChoice.choices,
        blank=True, null=True)
    supplier_item_id = models.CharField(_("Item identifier"), max_length=200, null=True, blank=True, unique=True)
    stage = models.CharField(
        verbose_name=_('Stage'),
        max_length=30, choices=ProductStage.choices,
        default=ProductStage.A_VIRTUAL)

    position = models.PositiveIntegerField(default=1)

    is_published = models.BooleanField(
        default=False, help_text=_('Publish this product'))
    dt_published = models.DateTimeField(
        blank=True, null=True, help_text=_('Publication date'))

    """
    SEO
    """

    meta_title = models.CharField(
        max_length=250, help_text=_('Product Meta title'),
        null=True, blank=True
    )
    meta_description = models.CharField(
        max_length=500, help_text=_('Product Meta description'),
        null=True, blank=True
    )
    meta_slug = models.SlugField(
        max_length=500, unique=True, db_index=True,
        null=True, blank=True
    )

    objects = ProductManager()

    @property
    def name_truncated(self):
        return truncate_str(capfirst(self.name), length=30)

    def get_hit_data(self):
        data = {
            'img': None,
            'cat_name': None,
            'cat_slug': None,
        }
        data.update({
            **super().get_hit_data(),
            'name': self.name,
            'slug': self.slug,
            'price': f'{self.get_price()}',
            'retail_price': f'{self.retail_price}',
            'sale_price': f'{self.sale_price}' if self.is_on_sale else None,
            'is_on_sale': self.is_on_sale,
            'is_oos': self.is_oos,
            'supplier': self.supplier,
            'supplier_item_id': self.supplier_item_id,
        })

        if self.category:
            data.update({
                'cat_name': self.category.name,
                'cat_slug': self.category.slug
            })

        if self.cover:
            # from pprint import pprint
            # pprint(self.cover.src.__dict__)
            # data['img'] = self.img_2_base64(self.cover.src.url)
            data['img'] = self.cover.src.url
        return data

    def img_2_base64(self, img_path):
        import base64

        with open(img_path) as image_file:
            return base64.b64encode(image_file.read())

    def get_availability(self):
        """
        IN = 'in stock'
        AV = 'available for order'
        OU = 'out of stock'
        DI = 'discontinued'
        """
        if not self.sizes.exists():
            return 'out of stock'
        return 'in stock'

    def get_quantity(self):
        if not self.sizes.exists():
            return 0
        return sum(size.quantity for size in self.sizes.all())

    def get_price(self):
        if self.is_on_sale:
            return self.sale_price
        return self.retail_price

    def get_condition(self):
        # a = 'new'
        # b = 'refurbished'
        # c = 'used'
        return 'new'

    def __str__(self):
        return capfirst(f'{self.name}')

    def save(self, *args, **kwargs):
        # if not self.pk:
        #     self.added_by = local.user if hasattr(local, 'user')

        if self.is_published and not self.dt_published:
            self.dt_published = timezone.now()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ('position', '-created', 'name')
        indexes = [
            models.Index(fields=['name', ], name='shopy_product_name_idx'),
        ]

    def supplier_item(self):
        return self.supplier_items.filter(product__slug=self.slug).first()

    def path(self, request=None):
        if(self.get_is_public()):
            path = reverse_lazy('shopy:product', args=[self.category.meta_slug, self.meta_slug])
            if request:
                return request.build_absolute_uri(path)
            return path

    def get_whatsapp_link(self, number, request):
        if not number or not request:
            return
        link = request.build_absolute_uri(self.path(request=request))
        param = urlencode({
            'text': f'Coucou!\nCet article est il toujours disponible?\n{link}',
        })

        return f'https://wa.me/{number}?{param}'

    def get_is_public(self):
        return self.category and self.category.is_published\
            and self.category.meta_slug\
            and self.meta_slug and self.is_published
