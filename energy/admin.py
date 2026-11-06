from django.contrib import admin
from .models import Appliance,Product,Customer,Quote,QuoteItem
@admin.register(Appliance)
class ApplianceAdmin(admin.ModelAdmin):
 list_display=('name','category','watts','active')
 list_editable=('watts','active')
 list_filter=('category','active')
 search_fields=('name',)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
 list_display=('name','category','brand','chemistry','price','active')
 list_editable=('price','active')
 list_filter=('category','chemistry','active')
 search_fields=('name','brand','model')
 fieldsets=[('Basic details',{'fields':('name','brand','model','category','unit','price','active')}),('Technical specifications',{'fields':('capacity_kva','voltage','ah','chemistry','wattage')}),('Quote defaults',{'fields':('default_qty',)})]
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
 list_display=('name','phone','email','created_at')
 search_fields=('name','email','phone')
class QuoteItemInline(admin.TabularInline):
 model=QuoteItem
 extra=0
 readonly_fields=('product_name','category','quantity','unit','unit_price','line_total')
 can_delete=False
@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
 list_display=('id','customer','created_at','total_watts','daily_kwh','estimated_total')
 list_filter=('created_at',)
 readonly_fields=('customer','created_at','total_watts','daily_kwh','estimated_total','calculation')
 inlines=[QuoteItemInline]
 def has_add_permission(self,request): return False
@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
 list_display=('quote','product_name','quantity','unit_price','line_total')
 readonly_fields=('quote','product_name','category','quantity','unit','unit_price','line_total')
 def has_add_permission(self,request): return False
