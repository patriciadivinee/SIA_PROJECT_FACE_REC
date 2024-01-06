from .models import Inventory, Requisition, Purchase_Order
from django.db.models import Q

def notification(request):
    low_stock_products = Inventory.objects.filter(Q(inv_qoh__lt=50) & ~Q(inv_qoh=0))
    out_stock_products = Inventory.objects.filter(inv_qoh = 0)
    pending_requisitions = Requisition.objects.filter(req_status='PENDING')
    pending_purchase_orders = Purchase_Order.objects.filter(po_status='PENDING')
    total_count = low_stock_products.count() + pending_requisitions.count() + pending_purchase_orders.count()

    context = {'total_count': total_count,
              'low_stock_products': low_stock_products,
              'pending_requisitions': pending_requisitions,
              'pending_purchase_orders': pending_purchase_orders,
              'out_stock_products': out_stock_products}
    
    return context