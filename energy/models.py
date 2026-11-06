from django.db import models
class Appliance(models.Model):
 name=models.CharField(max_length=120)
 category=models.CharField(max_length=80,default='General')
 watts=models.FloatField(default=100)
 active=models.BooleanField(default=True)
 def __str__(self): return f'{self.name} ({self.watts:g} W)'

class Product(models.Model):
 CATEGORY_CHOICES=[('inverter','Inverter'),('battery','Battery'),('panel','Solar panel'),('accessory','Accessory'),('service','Service')]
 CHEMISTRY_CHOICES=[('Lithium','Lithium'),('Tubular','Tubular'),('Gel','Gel'),('AGM','AGM')]
 name=models.CharField(max_length=160)
 brand=models.CharField(max_length=100,blank=True)
 category=models.CharField(max_length=30,choices=CATEGORY_CHOICES)
 model=models.CharField(max_length=100,blank=True)
 unit=models.CharField(max_length=30,default='unit')
 price=models.DecimalField(max_digits=14,decimal_places=2,default=0)
 capacity_kva=models.FloatField(null=True,blank=True)
 voltage=models.PositiveIntegerField(null=True,blank=True)
 ah=models.FloatField(null=True,blank=True)
 chemistry=models.CharField(max_length=40,choices=CHEMISTRY_CHOICES,default='Lithium')
 wattage=models.FloatField(null=True,blank=True)
 default_qty=models.PositiveIntegerField(default=0)
 active=models.BooleanField(default=True)
 def __str__(self): return self.name

class Customer(models.Model):
 name=models.CharField(max_length=160)
 email=models.EmailField(blank=True)
 phone=models.CharField(max_length=50,blank=True)
 address=models.CharField(max_length=255,blank=True)
 created_at=models.DateTimeField(auto_now_add=True)
 def __str__(self): return self.name

class Quote(models.Model):
 customer=models.ForeignKey(Customer,on_delete=models.PROTECT,related_name='quotes')
 created_at=models.DateTimeField(auto_now_add=True)
 total_watts=models.FloatField(default=0)
 daily_kwh=models.FloatField(default=0)
 estimated_total=models.DecimalField(max_digits=16,decimal_places=2,default=0)
 calculation=models.JSONField(default=dict)
 def __str__(self): return f'Quote #{self.pk} – {self.customer.name}'

class QuoteItem(models.Model):
 quote=models.ForeignKey(Quote,on_delete=models.CASCADE,related_name='items')
 product_name=models.CharField(max_length=160)
 category=models.CharField(max_length=30,blank=True)
 quantity=models.PositiveIntegerField(default=1)
 unit=models.CharField(max_length=30,default='unit')
 unit_price=models.DecimalField(max_digits=14,decimal_places=2,default=0)
 line_total=models.DecimalField(max_digits=16,decimal_places=2,default=0)
 def __str__(self): return f'{self.product_name} × {self.quantity}'

class Payment(models.Model):
    quote = models.ForeignKey(
        "Quote",
        on_delete=models.PROTECT,
        related_name="payments"
    )
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.reference} - {self.status}"

