from django.contrib import admin


from .models import Customer, Order, OrderItem, OrdersSetting, Cart

admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrdersSetting)
