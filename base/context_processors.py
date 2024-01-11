from .models import Inventory, Requisition, Purchase_Order
from django.db.models import Q
from django.contrib.auth.decorators import login_required

def notification(request):
    context = {}
    if request.user.is_authenticated:
        id = request.user.emp_id
        low_stock_products = Inventory.objects.filter(Q(inv_qoh__lt=50) & ~Q(inv_qoh=0))
        out_stock_products = Inventory.objects.filter(inv_qoh = 0)
        pending_requisitions = Requisition.objects.filter(req_status='PENDING')
        app_requisitions = Requisition.objects.filter(Q(req_status='APPROVED') & Q(emp_id = id))
        rej_requisitions = Requisition.objects.filter(Q(req_status='REJECTED') & Q(emp_id = id))
        rec_requisitions = Requisition.objects.filter(Q(req_status='RECEIVED') & Q(emp_id = id))
        pending_purchase_orders = Purchase_Order.objects.filter(po_status='PENDING')
        total_count = low_stock_products.count() + pending_requisitions.count() + pending_purchase_orders.count()
        emp_count = app_requisitions.count() + rej_requisitions.count() + rec_requisitions.count()

        context = {'total_count': total_count,
                'emp_count': emp_count,
                'low_stock_products': low_stock_products,
                'pending_requisitions': pending_requisitions,
                'app_requisitions': app_requisitions,
                'rej_requisitions': rej_requisitions,
                'rec_requisitions': rec_requisitions,
                'pending_purchase_orders': pending_purchase_orders,
                'out_stock_products': out_stock_products}
    
    return context