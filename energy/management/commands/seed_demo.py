from django.core.management.base import BaseCommand
from energy.models import Appliance,Product
class Command(BaseCommand):
 help='Insert example appliances and product prices (demonstration prices only).'
 def handle(self,*args,**kwargs):
  appliances=[('LED Light','Lighting',10),('Television','Entertainment',100),('Radio','Entertainment',30),('Washing Machine','Laundry',500),('Electric Iron','Laundry',1000),('Air Conditioner 1 HP','Cooling',900),('Standing Fan','Cooling',75),('Ceiling Fan','Cooling',60),('Refrigerator','Kitchen',150),('Laptop','Electronics',65),('Water Pump','Other',750),('Microwave','Kitchen',1200),('Deep Freezer','Kitchen',250)]
  for name,category,watts in appliances:Appliance.objects.get_or_create(name=name,defaults={'category':category,'watts':watts})
  products=[
   {'name':'1.5 kVA Inverter','category':'inverter','capacity_kva':1.5,'price':250000},
   {'name':'2.5 kVA Inverter','category':'inverter','capacity_kva':2.5,'price':380000},
   {'name':'3.5 kVA Inverter','category':'inverter','capacity_kva':3.5,'price':550000},
   {'name':'5 kVA Inverter','category':'inverter','capacity_kva':5,'price':850000},
   {'name':'10 kVA Inverter','category':'inverter','capacity_kva':10,'price':1850000},
   {'name':'12V 100Ah Lithium Battery','category':'battery','voltage':12,'ah':100,'chemistry':'Lithium','price':850000},
   {'name':'12V 200Ah Lithium Battery','category':'battery','voltage':12,'ah':200,'chemistry':'Lithium','price':1550000},
   {'name':'12V 200Ah Tubular Battery','category':'battery','voltage':12,'ah':200,'chemistry':'Tubular','price':620000},
   {'name':'12V 200Ah Gel Battery','category':'battery','voltage':12,'ah':200,'chemistry':'Gel','price':650000},
   {'name':'12V 200Ah AGM Battery','category':'battery','voltage':12,'ah':200,'chemistry':'AGM','price':670000},
   {'name':'550W Solar Panel','category':'panel','wattage':550,'price':180000},
   {'name':'DC Protection & Combiner Set','category':'accessory','price':95000,'default_qty':1},
   {'name':'AC Protection & Breaker Set','category':'accessory','price':75000,'default_qty':1},
   {'name':'Mounting & Installation Materials','category':'accessory','price':150000,'default_qty':1},
   {'name':'Installation & Commissioning','category':'service','price':200000,'default_qty':1},
  ]
  for row in products:
   name=row.pop('name');Product.objects.get_or_create(name=name,defaults=row)
  self.stdout.write(self.style.SUCCESS('Demo catalogue created. Replace all example prices with supplier quotations.'))
