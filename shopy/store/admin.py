from django.contrib import admin

from .models import (
    Product, ProductImage,
    Category, SupplierOrder, SupplierItem
)

admin.site.register(ProductImage)
admin.site.register(Category)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    model = Product


admin.site.register(SupplierItem)
admin.site.register(SupplierOrder)
