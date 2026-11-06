import io,json
from django.db import transaction
from django.http import JsonResponse,HttpResponse,Http404
from django.shortcuts import render,get_object_or_404
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from .models import Appliance,Product,Customer,Quote,QuoteItem
from .calculator import calculate_system

@ensure_csrf_cookie
def home(request):
 return render(request,'index.html',{'appliance_catalog':[{'id':a.id,'name':a.name,'watts':a.watts,'category':a.category} for a in Appliance.objects.filter(active=True).order_by('category','name')]})
@require_GET
def catalog(request):
 return JsonResponse({'appliances':[{'id':a.id,'name':a.name,'watts':a.watts,'category':a.category} for a in Appliance.objects.filter(active=True)],'products':[{'id':p.id,'name':p.name,'category':p.category,'price':float(p.price),'chemistry':p.chemistry} for p in Product.objects.filter(active=True)]})
def compute(payload):
 return calculate_system(payload,{a.id:a for a in Appliance.objects.filter(active=True)},list(Product.objects.filter(active=True)))
@require_POST
def calculate(request):
 try:
  result=compute(json.loads(request.body))
  return JsonResponse({'success':True,'result':result})
 except (ValueError,TypeError,KeyError,OverflowError,json.JSONDecodeError) as exc:
  return JsonResponse({'success':False,'error':str(exc)},status=400)
@require_POST
def create_quote(request):
 try:
  payload=json.loads(request.body)
  customer_data=payload.get('customer',{})
  name=str(customer_data.get('name') or '').strip()
  if not name: raise ValueError('Customer name is required.')
  result=compute(payload)
  if not result['inverter'] or not result['battery'] or not result['solar_panel']:
   raise ValueError('A complete quotation requires a compatible inverter, battery and solar panel in the catalogue.')
  with transaction.atomic():
   customer=Customer.objects.create(name=name,email=customer_data.get('email',''),phone=customer_data.get('phone',''),address=customer_data.get('address',''))
   quote=Quote.objects.create(customer=customer,total_watts=result['total_watts'],daily_kwh=result['daily_kwh'],estimated_total=result['estimated_total'],calculation=result)
   QuoteItem.objects.bulk_create([QuoteItem(quote=quote,product_name=x['name'],category=x['category'],quantity=x['quantity'],unit=x['unit'],unit_price=x['unit_price'],line_total=x['line_total']) for x in result['items']])
  return JsonResponse({'success':True,'quote_id':quote.id,'pdf_url':f'/quote/{quote.id}/pdf/'})
 except (ValueError,TypeError,KeyError,OverflowError,json.JSONDecodeError) as exc:
  return JsonResponse({'success':False,'error':str(exc)},status=400)
@require_GET
def quote_pdf(request,quote_id):
 quote=get_object_or_404(Quote,pk=quote_id)
 result=quote.calculation
 buf=io.BytesIO()
 doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=18*mm)
 styles=getSampleStyleSheet()
 story=[Paragraph('POWERSOLUTION - ENERGY ASSESSMENT & QUOTATION',styles['Title']),Spacer(1,8),Paragraph(f'Quotation #{quote.id} | {quote.created_at:%d %b %Y}',styles['Normal']),Paragraph(f'Customer: {quote.customer.name}',styles['Normal']),Spacer(1,12),Paragraph('System assessment',styles['Heading2'])]
 summary=[['Connected load',f'{result["total_watts"]:,} W'],['Daily energy',f'{result["daily_kwh"]} kWh'],['Required inverter',f'{result["required_inverter_kva"]} kVA'],['Battery backup target',f'{result["backup_hours"]} hours'],['PV array estimate',f'{result["pv_required_w"]:,} W']]
 table=Table(summary,colWidths=[70*mm,85*mm]);table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.4,colors.lightgrey),('PADDING',(0,0),(-1,-1),7)]));story.extend([table,Spacer(1,12),Paragraph('Itemised equipment and services (NGN)',styles['Heading2'])])
 data=[['Description','Qty','NGN/unit','NGN total']]
 for x in result['items']: data.append([Paragraph(x['name'],styles['BodyText']),str(x['quantity']),f'{x["unit_price"]:,.2f}',f'{x["line_total"]:,.2f}'])
 data.append(['','','ESTIMATED TOTAL',f'{result["estimated_total"]:,.2f}'])
 table=Table(data,colWidths=[75*mm,18*mm,35*mm,37*mm],repeatRows=1)
 table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#153B5B')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.lightgrey),('PADDING',(0,0),(-1,-1),6),('ALIGN',(1,1),(-1,-1),'RIGHT')]))
 story.extend([table,Spacer(1,12),Paragraph('Engineering notes',styles['Heading2'])])
 for warning in result['warnings']:story.append(Paragraph('- '+warning,styles['BodyText']))
 story.append(Spacer(1,12));story.append(Paragraph('Indicative estimate only; confirm compatibility, surge loads, installation scope and current supplier prices.',styles['Italic']))
 doc.build(story)
 response=HttpResponse(buf.getvalue(),content_type='application/pdf')
 response['Content-Disposition']=f'attachment; filename="PowerSolution-Quote-{quote.id}.pdf"'
 return response

def privacy_policy(request):
    return render(request,"privacy_policy.html")
