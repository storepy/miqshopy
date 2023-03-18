

# from django.utils.text import slugify


from .m_category import Category  # noqa

from .m_product_size_attr import ProductAttribute, ProductSize
from .m_product import Product, ProductStage, ProductStages

from .m_proxy import ProductImage, ProductPage, CategoryPage

from .m_setting import ShopSetting

from .m_supplier import SupplierOrder, SupplierItem, SUPPLIER_MAP
from .m_supplier import SupplierChoice, SupplierChoices

from .m_analytics import ShopHit
from .m_analytics import ProductHit, CategoryHit
