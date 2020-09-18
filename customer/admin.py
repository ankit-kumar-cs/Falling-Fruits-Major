from django.contrib import admin
from .models import Account,Profile,Product,Farm,Order,OrderItem,Address
# Register your models here.
admin.site.register(Account)
admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(Farm)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)