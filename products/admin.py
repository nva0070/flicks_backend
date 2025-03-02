from django.contrib import admin
from .models import Product

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title','brand','product_category')
    list_filter=('product_category','brand','gender')
    search_fields=('title','brand','description')
    
admin.site.register(Product,ProductAdmin)
