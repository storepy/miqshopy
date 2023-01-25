

# from django.utils.text import slugify


from .m_category import Category  # noqa

from .productSizeAttrModels import ProductAttribute, ProductSize
from .productModel import Product, ProductStage, ProductStages

from .proxyModels import ProductImage, ProductPage, CategoryPage

from .settingModel import ShopSetting

from .supplierModels import SupplierOrder, SupplierItem, SUPPLIER_MAP
from .supplierModels import SupplierChoice, SupplierChoices

from .analyticsModels import ShopHit
from .analyticsModels import ProductHit, CategoryHit
