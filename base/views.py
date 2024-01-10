from datetime import timedelta
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.http import HttpResponseBadRequest
from django.utils.http import urlsafe_base64_decode
import datetime
import re
import json
from django.db.models import Sum, F, Count
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CategoryForm
from .models import *
from django.core.files.storage import default_storage
# from .models import Product, Category, Inventory, Employee, CustomUser, Requisition, RequisitionItem, Contact, Supplier, Supplier_Item
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as login, authenticate, logout
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from .decorators import emp_access
from django.core.exceptions import ValidationError
import random
import string
import os

# Create your views here.
@login_required(login_url='user_login')
def home(request):
    employee = request.user.emp
    thirty_days_ago = timezone.now() - timedelta(days=30) #for top 5 most requested product
    
    # Querying top requested items in the last 30 days
    top_requested_items = RequisitionItem.objects.filter(
        req_id__req_created_at__gte=thirty_days_ago,
        req_id__req_created_at__lte=timezone.now(),
    ).exclude(req_id__req_status='REJECTED').values('prod_id__prod_name') \
        .annotate(total_requested=Sum('req_qty')).order_by('-total_requested')[:5]


    # Data for the first chart (from Product table, grouped by prod_status)
    product_counts = Product.objects.values('prod_status').annotate(total=Count('prod_status'))
    labels1 = []
    data1 = []
    colors1 = ['rgba(255, 99, 132, 0.8)', 'rgba(54, 162, 235, 0.8)', 'rgba(255, 206, 86, 0.8)']

    for entry in product_counts:
        labels1.append(entry['prod_status'])
        data1.append(entry['total'])

    labels_json1 = json.dumps(labels1)
    data_json1 = json.dumps(data1)
    colors_json1 = json.dumps(colors1)

    # Data for the second chart (from Product table, grouped by Cat_id)
    category_counts = Product.objects.values('cat_id').annotate(total=Count('cat_id'))
    labels2 = []
    data2 = []
    colors2 = ['rgba(75, 192, 192, 0.8)', 'rgba(153, 102, 255, 0.8)', 'rgba(255, 159, 64, 0.8)']

    for entry in category_counts:
        category = Category.objects.get(cat_id=entry['cat_id'])  # Assuming Category model has 'name' field
        labels2.append(category.cat_name)
        data2.append(entry['total'])

    labels_json2 = json.dumps(labels2)
    data_json2 = json.dumps(data2)
    colors_json2 = json.dumps(colors2)

    products = Product.objects.all()
    labels3 = []
    data3 = []
    colors3 = []

    products = Product.objects.all()
    labels3 = []
    data3 = []
    colors3 = []

    for product in products:
        labels3.append(product.prod_name)
        try:
            inventory = Inventory.objects.get(prod_id=product.prod_id)
            data3.append(inventory.inv_qoh)
        except Inventory.DoesNotExist:
            # If Inventory doesn't exist for this product, handle it accordingly
            data3.append(0)  # Set a default value, like 0
        colors3.append('#{:06x}'.format(random.randint(0, 256**3-1)))

    print("Labels:", labels3)  # Check labels in the console
    print("Data:", data3)  # Check data in the console

    labels_json3 = json.dumps(labels3)
    data_json3 = json.dumps(data3)
    colors_json3 = json.dumps(colors3)

    #for passing sa katung labels sa top 5
    labels = []
    data = []
    for item in top_requested_items:
        labels.append(item['prod_id__prod_name'])
        data.append(item['total_requested'])

    labels_json = json.dumps(labels)
    data_json = json.dumps(data)

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(emp_status=True).count()
    inactive_employees = Employee.objects.filter(emp_status=False).count()

    low_stock_products = Inventory.objects.filter(inv_qoh__lt=50)
    pending_requisitions = Requisition.objects.filter(req_status='PENDING')
    pending_purchase_orders = Purchase_Order.objects.filter(po_status='PENDING')
    total_count = low_stock_products.count() + pending_requisitions.count() + pending_purchase_orders.count()

    return render(request, 'base/home.html', {
        'labels1': labels_json1,
        'data1': data_json1,
        'colors1': colors_json1,
        'labels2': labels_json2,
        'data2': data_json2,
        'colors2': colors_json2,
        'labels3': labels_json3,
        'data3': data_json3,
        'colors3': colors_json3,
        'top_requested_items': top_requested_items,
        'labels': labels_json,
        'data': data_json,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
        'user': request.user, 'employee': employee,
        'nav': 'home',
        'total_count': total_count,
        'low_stock_products': low_stock_products,
        'pending_requisitions': pending_requisitions,
        'pending_purchase_orders': pending_purchase_orders
    })

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation

    password = ''.join(random.choice(characters) for _ in range(length))

    return password

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('emailaddress')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            print("Authentication failed")
            return render(request, 'base/login.html')

    superadmin_ = CustomUser.objects.filter(is_superuser = True).count()

    return render(request, 'base/login.html', {'superadmin': superadmin_})

def logout_emp(request):
    logout(request)
    return redirect("user_login")

@login_required(login_url='user_login')
@csrf_exempt
def create_employee_and_user(request, is_superuser=False):
    try:
        if request.method == 'POST':
            emp_fname = request.POST.get('firstname')
            emp_lname = request.POST.get('lastname')
            emp_gender = request.POST.get('gender')
            emp_address = request.POST.get('address')
            emp_dob = request.POST.get('dob')
            emp_mobile = request.POST.get('mobile')
            emp_email = request.POST.get('emailaddress')
            emp_password = generate_random_password()
            encrypted = emp_password

            if 'imagefile' in request.FILES:
                emp_image = request.FILES['imagefile']
                
            else:
                messages.error(request, 'Image is required.')
                return redirect('register_acc')

            
            if not any([emp_fname, emp_lname, emp_gender, emp_address, emp_dob, emp_mobile, emp_email]):
                messages.error(request, 'All fields are required.')
                return redirect('register_acc')
            
            if not emp_fname.strip() or not emp_lname.strip():
                messages.error(request, "Firstname and Lastname are required.")
                return redirect('register_acc')
            
            if re.search(r'\s{2,}', emp_fname) or re.search(r'\s{2,}', emp_lname):
                messages.error(request, "Consecutive whitespaces are not allowed in Firstname or Lastname.")
                return redirect('register_acc')

            if re.search(r'[^a-zA-Z\s]', emp_fname) or re.search(r'[^a-zA-Z\s]', emp_lname):
                messages.error(request, "Special characters are not allowed in Firstname or Lastname.")
                return redirect('register_acc')

            if emp_gender not in ["Male", "Female"]:
                messages.error(request, "Gender field required")
                return redirect('register_acc')

            if any(char.isdigit() for char in emp_fname) or any(char.isdigit() for char in emp_lname):
                messages.error(request, "First or Last names cannot contain digits")
                return redirect('register_acc')

            if not re.match(r'^(\+?63|0)9\d{9}$', emp_mobile):
                messages.error(request, "Invalid mobile number format")
                return redirect('register_acc')

            if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', emp_email):
                messages.error(request, "Invalid Gmail email format")
                return redirect('register_acc')
            
            


            employee = Employee.objects.create(emp_fname=emp_fname, emp_lname=emp_lname,
                                               emp_gender=emp_gender, emp_dob=emp_dob, emp_mobile=emp_mobile,
                                               emp_email=emp_email, emp_password=emp_password, emp_image=emp_image,
                                               emp_address=emp_address)
            employee.save()

            user = CustomUser.objects.create(email=emp_email, first_name=emp_fname,
                                            last_name=emp_lname, emp_id=employee.emp_id, is_staff=is_superuser,
                                            is_superuser=is_superuser, emp_access=is_superuser, is_active=True)

            

            user.set_password(encrypted)
            user.save()
            send_welcome_email(employee)

            messages.success(request, "Registration successful.")
            return render(request, 'base/register.html')

    except IntegrityError:
        messages.error(request, 'Email already exists')

    return redirect('register_acc')

def superview(request):
    return render(request, 'base/register_admin.html')
def create_superuser(request):
    try:
        if request.method == 'POST':
            emp_fname = request.POST.get('firstname')
            emp_lname = request.POST.get('lastname')
            emp_gender = request.POST.get('gender')
            emp_address = request.POST.get('address')
            emp_dob = request.POST.get('dob')
            emp_mobile = request.POST.get('mobile')
            emp_email = request.POST.get('emailaddress')
            emp_pass = request.POST.get('password')
            conpass = request.POST.get('conpass')

            if 'imagefile' in request.FILES:
                emp_image = request.FILES['imagefile']
                
            else:
                messages.error(request, 'Image is required.')
                return redirect('superview')
            
            if not any([emp_fname, emp_lname, emp_gender, emp_address, emp_dob, emp_mobile, emp_email]):
                messages.error(request, 'All fields are required.')
                return redirect('superview')
            
            if not emp_fname.strip() or not emp_lname.strip():
                messages.error(request, "Firstname and Lastname are required.")
                return redirect('superview')
            
            if re.search(r'\s{2,}', emp_fname) or re.search(r'\s{2,}', emp_lname):
                messages.error(request, "Consecutive whitespaces are not allowed in Firstname or Lastname.")
                return redirect('superview')

            if re.search(r'[^a-zA-Z\s]', emp_fname) or re.search(r'[^a-zA-Z\s]', emp_lname):
                messages.error(request, "Special characters are not allowed in Firstname or Lastname.")
                return redirect('superview')

            if emp_gender not in ["Male", "Female"]:
                messages.error(request, "Gender field required")
                return redirect('superview')

            if any(char.isdigit() for char in emp_fname) or any(char.isdigit() for char in emp_lname):
                messages.error(request, "First or Last names cannot contain digits")
                return redirect('superview')

            if not re.match(r'^(\+?63|0)9\d{9}$', emp_mobile):
                messages.error(request, "Invalid mobile number format")
                return redirect('superview')

            if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', emp_email):
                messages.error(request, "Invalid Gmail email format")
                return redirect('superview')
            
            if emp_pass != conpass:
                messages.error(request, "Password does not match the confirm password.")
                return redirect('superview')

            employee = Employee.objects.create(emp_fname=emp_fname, emp_lname=emp_lname,
                                            emp_gender=emp_gender, emp_dob=emp_dob, emp_mobile=emp_mobile,
                                            emp_email=emp_email, emp_password=emp_pass, emp_image=emp_image,
                                            emp_address=emp_address)
            employee.save()

            user = CustomUser.objects.create(email=emp_email, first_name=emp_fname,
                                            last_name=emp_lname, emp_id=employee.emp_id, is_staff=True,
                                            is_superuser=True, emp_access=True, is_active=True)

            

            user.set_password(emp_pass)
            user.save()
            send_welcome_email(employee)

            messages.success(request, "Registration successful.")
            return redirect('user_login')

    except IntegrityError:
        messages.error(request, 'Email already exists')
        return redirect('superview')

def register(request):
    return create_employee_and_user(request, is_superuser=False)

def register_superuser(request):
    return create_employee_and_user(request, is_superuser=True)

def send_welcome_email(employee):
    message = (
        'Dear ' + str(employee.emp_lname) + ', \n' +
        'We are thrilled to welcome you to Beautyki! ' +
        'This email is to confirm that an account has been created for you by our administrator. ' +
        'Below are the details for your BeautyKi account:\n' +
        'Account Information:\n' +
        'Name: ' + str(employee.emp_fname) + ' ' + str(employee.emp_lname) + '\n' +
        'Email Address: ' + str(employee.emp_email) + '\n' +
        'Temporary Password: ' + str(employee.emp_password) + '\n'
    )

    try:
        send_mail(
            'Welcome to Beautyki - Your Account Details', message,
            settings.EMAIL_HOST_USER,  # Sender Email,
            [employee.emp_email],
            fail_silently=False
        )
    except Exception as e:
        print('Error sending welcome email:', e)

@login_required(login_url='user_login')
def register_acc(request):
    return render(request, 'base/register.html', {'nav': 'employee'})

@login_required(login_url='user_login')
@emp_access
def viewaccount(request):
    superusers = CustomUser.objects.filter(is_superuser=True)
    employees = Employee.objects.exclude(customuser__in=superusers)
    context = {'employees': employees, 'nav': 'employee'}
    return render(request, 'base/employee_lists.html', context)

@login_required(login_url='user_login')
def edit_employee(request, emp_id):
    employee = Employee.objects.get(emp_id=emp_id)
    user = employee.customuser  
    user_copy = user.__class__.objects.get(pk=user.pk)
    context = {"employee": employee, "user_copy": user_copy, 'this_user': user, 'nav': 'employee'}

    return render(request, 'base/updateaccount.html', context)

@login_required(login_url='user_login')
def delete(request, emp_id):
    employee = get_object_or_404(Employee, emp_id = emp_id)
    user = CustomUser.objects.filter(emp=employee).first()

    if user:
        user.delete()
    employee.delete()
    return redirect('viewaccount')

@login_required(login_url='user_login')
def update(request, emp_id):
    try:
        employee = Employee.objects.get(emp_id=emp_id)
        user = employee.customuser
        user_copy = user.__class__.objects.get(pk=user.pk)
        context = {"employee": employee, 'this_user': user, "user_copy": user_copy, 'user_copy': user, 'user': request.user}

        new_image = None
        if request.method == 'POST':
            employee.emp_fname = request.POST.get('firstname')
            employee.emp_lname = request.POST.get('lastname')
            employee.emp_gender = request.POST.get('gender')
            employee.emp_dob = request.POST.get('dob')
            employee.emp_address = request.POST.get('address')
            employee.emp_mobile = request.POST.get('mobile')
            employee.emp_email = request.POST.get('emailaddress')
            employee.emp_status = request.POST.get('status') == 'true'

            if 'imagefile' in request.FILES:
                new_image = request.FILES['imagefile']

                if employee.emp_image:
                    default_storage.delete(employee.emp_image.name)
                employee.emp_image.save(new_image.name, new_image)


            user.email = employee.emp_email
            user.first_name = employee.emp_fname
            user.last_name = employee.emp_lname
            user.is_active = request.POST.get('status') == 'true'
            user.is_staff = request.POST.get('staff_admin_access') == 'true'
            user.is_superuser = request.POST.get('superadmin') == 'true'
            user.emp_access = request.POST.get('emp_access') == 'true'

            # Validate email uniqueness
            if CustomUser.objects.exclude(pk=user.pk).filter(email=employee.emp_email).exists():
                messages.error(request, "Email is already taken")
                return redirect('update_employee', emp_id=employee.emp_id)

            # Additional validation checks
            try:
                validate_email(employee.emp_email)
            except ValidationError:
                messages.error(request, "Invalid email format")
                return redirect('update_employee', emp_id=employee.emp_id)

            if not employee.emp_fname.strip() or not employee.emp_lname.strip():
                messages.error(request, "Firstname and Lastname are required.")
                return redirect('update_employee', emp_id=employee.emp_id)
            
            if re.search(r'\s{2,}', employee.emp_fname) or re.search(r'\s{2,}', employee.emp_lname):
                messages.error(request, "Consecutive whitespaces are not allowed in Firstname or Lastname.")
                return redirect('update_employee', emp_id=employee.emp_id)

            if re.search(r'[^a-zA-Z\s]', employee.emp_fname) or re.search(r'[^a-zA-Z\s]', employee.emp_lname):
                messages.error(request, "Special characters are not allowed in Firstname or Lastname.")
                return redirect('update_employee', emp_id=employee.emp_id)

            if employee.emp_gender not in ["Male", "Female"]:
                messages.error(request, "Invalid gender value")
                return redirect('update_employee', emp_id=employee.emp_id)

            if any(char.isdigit() for char in employee.emp_fname) or any(char.isdigit() for char in employee.emp_lname):
                messages.error(request, "First or Last names cannot contain digits")
                return redirect('update_employee', emp_id=employee.emp_id)

            if not re.match(r'^(\+?63|0)9\d{9}$', employee.emp_mobile):
                messages.error(request, "Invalid mobile number format")
                return redirect('update_employee', emp_id=employee.emp_id)

            if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', employee.emp_email):
                messages.error(request, "Invalid Gmail email format")
                return redirect('update_employee', emp_id=employee.emp_id)

            # Save changes
            employee.save()
            user.save()
            messages.success(request, "Account has been updated successfully")
            return redirect('update_employee', emp_id=employee.emp_id)

        return render(request, 'base/updateaccount.html', context)

    except IntegrityError:
        messages.error(request, "Firstname, Lastname, and DOB must be unique.")
        return redirect('update_employee', emp_id=employee.emp_id)

@login_required(login_url='user_login')
def employee_details(request, emp_id):
    try:
        employee = Employee.objects.get(emp_id=emp_id)
    except Employee.DoesNotExist:
        return HttpResponse('Employee not found', status=404)

    context = {'employee': employee}
    return render(request, 'base/employeedeets.html', context)

@login_required(login_url='user_login')
def retrieve_view(request):
    employees = Employee.objects.filter(emp_status = False)
    context ={'employees': employees}
    return render(request, 'base/retrieve_emp.html', context)

@login_required(login_url='user_login')
def retrieve_emp(request, emp_id):
    employee = get_object_or_404(Employee, emp_id=emp_id)
    user = CustomUser.objects.filter(emp=employee).first()

    if user:
        # Set is_active to True for the user
        user.is_active = True
        user.save()

    # Set emp_status to True for the employee
    employee.emp_status = True
    employee.save()
    return redirect('viewaccount')

@login_required(login_url='user_login')
def product_list(request):
    prod_list = Product.objects.all()

    nav = 'product'

    return render(request, 'base/product_list.html', {'prods': prod_list, 'nav': nav})

def purchase_history(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    supplier_company = request.GET.get('supplier_company')

    purchase_history = Purchase_Order.objects.all()
    suppliers = Supplier.objects.all()

    if supplier_company:
        purchase_history = purchase_history.filter(sup_id__sup_company=supplier_company)

        if not start_date and not end_date:
            # If no date range specified, show all requisitions for the selected supplier
            return render(request, 'base/purchase_history.html', {'purchase_history': purchase_history, 'suppliers': suppliers})

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        purchase_history = purchase_history.filter(po_created_at__date__range=(start_date, end_date))

    if not suppliers:
        suppliers = []

    return render(request, 'base/purchase_history.html', {'purchase_history': purchase_history, 'suppliers': suppliers})

def custom_title_format(title):
    words = title.split()
    modified_words = []

    for word in words:
        if "'" in word:
            parts = word.split("'")
            modified_word = parts[0] + "'" + parts[1].lower()
            modified_words.append(modified_word)
        else:
            modified_words.append(word)

    return ' '.join(modified_words)

@login_required(login_url='user_login')
def add_product(request):
    if request.method == 'POST':
        brand_ = request.POST.get('prod_brand').strip()
        brand = custom_title_format(brand_)
        name_ = request.POST.get('prod_name').strip()
        name = custom_title_format(name_)
        desc = request.POST.get('prod_desc').strip()
        cat = request.POST.get('cat_id')

        try:
            if not brand.isspace() and not name.isspace() and not desc.isspace() and not brand.isdigit() and not name.isdigit() and not desc.isdigit() and cat != None and brand != '' and name != '' and desc != '':
                prod = Product()
                unit = request.POST.get('unit')
                prod_pack_size = request.POST.get('prod_pack_size')
                prod.prod_brand = brand.title()
                prod.prod_name = name.title()
                prod.prod_price = request.POST.get('prod_price')
                prod.prod_pack_size = f"{prod_pack_size}{unit}"
                prod.prod_desc = desc.lower()
                cat_id = cat

                category_instance = Category.objects.get(pk=cat_id)

                prod.cat_id = category_instance

                prod.save()
                messages.success(request, 'Product is added successfully!')

                return redirect('products')
            else:
                messages.error(request, 'Please enter valid data.')
                return redirect('view_form_product')
        except IntegrityError:
                messages.error(request, 'Product already exists.')
                return redirect('view_form_product')
    else:
        return render(request, 'base/add_product.html')

@login_required(login_url='user_login')
def view_form_product(request):
    cat_list = Category.objects.all()

    return render(request, 'base/add_product.html', {'cat_list': cat_list, 'nav': 'product'})

@login_required(login_url='user_login')
def edit_product(request, prod_id):
    cat_list = Category.objects.all()

    try:
        prod = Product.objects.get(pk=prod_id)
        size = int(re.sub(r'[^0-9]', '', prod.prod_pack_size))
        unit_ = re.sub(r'[0-9]', '', prod.prod_pack_size)
        cat = prod.cat_id.cat_id
        
        pack_size = {
            'size': size,
            'unit_': unit_,
            'cat': cat,
        }

        if request.method == 'POST':
            brand_ = request.POST.get('prod_brand').strip()
            brand = custom_title_format(brand_)
            name_ = request.POST.get('prod_name').strip()
            name = custom_title_format(name_)
            desc = request.POST.get('prod_desc').strip()
            cat = request.POST.get('cat_id')
            unit = request.POST.get('unit')
            stat = request.POST.get('status')
            try:
                inv = Inventory.objects.get(prod_id = prod)

                if stat == 'Discontinued' and inv.inv_qoh != 0:
                    messages.error(request, 'Cannot discontinue product with more than 0 stock.')
                else:
                    if not brand.isspace() and not name.isspace() and not desc.isspace() and not brand.isdigit() and not name.isdigit() and not desc.isdigit() and cat != None and brand != '' and name != '' and desc != '':
                        prod_pack_size = request.POST.get('prod_pack_size')
                        prod.prod_brand = brand.title()
                        prod.prod_name = name.title()
                        prod.prod_price = request.POST.get('prod_price')
                        prod.prod_pack_size = f"{prod_pack_size}{unit}"
                        prod.prod_desc = desc.lower()
                        prod.prod_status = stat
                        cat_id = request.POST.get('cat_id')

                        category_instance = Category.objects.get(pk=cat_id)

                        prod.cat_id = category_instance

                        prod.save()
                        messages.success(request, 'Product is updated successfully!')

                        return redirect('products')
                    else:
                        messages.error(request, 'Please enter valid data.')
                        return redirect('edit_product', prod_id)
            except Inventory.DoesNotExist:
                if not brand.isspace() and not name.isspace() and not desc.isspace() and not brand.isdigit() and not name.isdigit() and not desc.isdigit() and cat != None and brand != '' and name != '' and desc != '':
                    prod_pack_size = request.POST.get('prod_pack_size')
                    prod.prod_brand = brand.title()
                    prod.prod_name = name.title()
                    prod.prod_price = request.POST.get('prod_price')
                    prod.prod_pack_size = f"{prod_pack_size}{unit}"
                    prod.prod_desc = desc.lower()
                    prod.prod_status = stat
                    cat_id = request.POST.get('cat_id')

                    category_instance = Category.objects.get(pk=cat_id)

                    prod.cat_id = category_instance

                    prod.save()
                    messages.success(request, 'Product is updated successfully!')

                    return redirect('products')
                else:
                    messages.error(request, 'Please enter valid data.')
                    return redirect('edit_product', prod_id)
            except IntegrityError:
                messages.error(request, 'Product already exists.')
                return redirect('edit_product', prod_id)

        return render(request, 'base/edit_product.html', {'cat_list': cat_list, 'prod_deets': prod, 'pack_size': pack_size, 'nav': 'product'})
    except Product.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')
def delete_product(request, prod_id):
    try:
        prod = Product.objects.get(prod_id = prod_id)
        try:
            inv = Inventory.objects.get(prod_id = prod)
            if inv.inv_qoh != 0:
                messages.error(request, 'Cannot discontinue product with more than 0 stock.')
            else:
                prod.prod_status = 'Discontinued'
                prod.save()
            return redirect('products')
        except Inventory.DoesNotExist:
            prod.prod_status = 'Discontinued'
            prod.save()
            return redirect('products')
    except Product.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')    
def delete_category(request, cat_id):
    try:
        prod = Category.objects.get(cat_id = cat_id)
        prod.delete()
        return redirect('category_view')
    except Category.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')
def category_view(request):
        
    cat_prod = Product.objects.all()
    cat_list = Category.objects.all()

    nav = 'category'

    return render(request, 'base/category.html', {'cat_list': cat_list, 'cat_prod' : cat_prod, 'nav': nav})

@login_required(login_url='user_login')
def category_add(request):
    if request.method == 'POST':
        if 'save' in request.POST:
            try:
                forms = CategoryForm(request.POST)
                cate = request.POST.get('cat_name').strip()
                if forms.is_valid() and not cate.isdigit():
                    category = Category()
                    category.cat_name = cate.title()
                    category.save()
                    messages.success(request, 'Category is added successfully!')
                else:
                    messages.error(request, 'Please enter valid data.')
            except IntegrityError:
                messages.error(request, 'Category already exists.')
        elif 'edit' in request.POST:
            try:
                cat_id = int(request.POST.get('passed_id'))
                cname = request.POST.get('edited_cname').strip()

                if not cname.isspace() and not cname.isdigit() and cname != '':
                    cat = Category.objects.get(pk=cat_id)

                    cat.cat_name = cname.title()
                    cat.save()
                    messages.success(request, 'Category is updated successfully!')
                else:
                    messages.error(request, 'Please enter valid data.')
            except IntegrityError:
                messages.success(request, 'Category already exists.')
        return redirect('/products/category')
    else:
        forms = CategoryForm()

@login_required(login_url='user_login')
def product_details(request, prod_id):
    try:
        prod = Product.objects.get(pk=prod_id)

        return render(request, 'base/product_details.html', {'prod': prod, 'nav': 'product'} )
    except Product.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')
@csrf_exempt
def search_product(request):
    if request.method == 'POST':
        search_id = request.POST.get('search_id')
        try:
            prod = Product.objects.get(pk=search_id)
            data = {'brand': prod.prod_brand, 'name': prod.prod_name, 'size': prod.prod_pack_size, 'price': prod.prod_price, 'desc': prod.prod_desc}  # Replace 'some_field' with the field you want to send in the response
            return JsonResponse(data)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'})
    return JsonResponse({'error': 'Invalid request method'})

@login_required(login_url='user_login')
# @emp_access
def add_inventory(request):
    if request.method == 'POST':
        fk = request.POST.get('search_id')
        inv_qoh = request.POST.get('prod_stock')
        try:
            inv_item = Inventory.objects.get(prod_id=fk)
            new_stock = inv_item.inv_qoh + int(inv_qoh)
            inv_item.inv_qoh = new_stock
            inv_item.save()
            
            # messages.error(request,'Product already exist in inventory')
        except Inventory.DoesNotExist:
            inv = Inventory(request.POST)

            if int(inv_qoh) <= 50:
                inv.inv_status = 'Low Stock'

            prod_id = Product.objects.get(pk=fk)
            prod_id.prod_status = 'Available'

            inv.inv_qoh = inv_qoh
            inv.prod_id = prod_id

            prod_id.save()
            inv.save()
    
    return redirect('/products/inventory/' + 'in stock')



@login_required(login_url='user_login')
# @emp_access
def inventory(request, inv_status):
    status = inv_status.title()
    if inv_status == 'in stock':
        inv_list = Inventory.objects.all()
    else:
        inv_list = Inventory.objects.filter(inv_status = status)

    all = Inventory.objects.all().count()
    low = Inventory.objects.filter(inv_status = 'Low Stock').count()
    out = Inventory.objects.filter(inv_status = 'Out Of Stock').count()

    context = {
        'inventory': inv_list,
        'status': status,
        'all': all,
        'low': low,
        'out': out,
        'nav': 'inventory'
    }

    return render(request, 'base/inventory_stock.html', context)

@login_required(login_url='user_login')
def requisition(request):
    prod = Product.objects.all()

    for pcat in prod:
        try:
            inventory_data = Inventory.objects.get(prod_id_id=pcat.prod_id)  
            pcat.inv_qoh = inventory_data.inv_qoh  
        except Inventory.DoesNotExist:
            pcat.inv_qoh = None

    return render(request, 'base/create_requisition.html', {'prod': prod, 'nav': 'requisition'})

@login_required(login_url='user_login')
def emp_requisition(request, req_status):
    status = req_status.upper()
    try:
        emp = CustomUser.objects.get(email=request.user)
        emp_id = Employee.objects.get(emp_id=emp.emp_id)
        req = Requisition.objects.filter(Q(emp_id=emp_id) & Q(req_status=status))

        pending = Requisition.objects.filter(Q(emp_id=emp_id) & Q(req_status='PENDING')).count()
        approved = Requisition.objects.filter(Q(emp_id=emp_id) & Q(req_status='APPROVED')).count()
        rejected = Requisition.objects.filter(Q(emp_id=emp_id) & Q(req_status='REJECTED')).count()
        received = Requisition.objects.filter(Q(emp_id=emp_id) & Q(req_status='RECEIVED')).count()

        title_case = status.title()

        context = {
            'req': req,
            'status': title_case,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'received': received,
            'nav': 'requisition'
        }

        return render(request, 'base/employee_requisition.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee does not exist')
        
    return render(request, 'base/employee_requisition.html')

@login_required(login_url='user_login')
@csrf_exempt
def add_req(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            date = data.get('edd')
            emp = CustomUser.objects.get(email=request.user)
            emp_id = Employee.objects.get(emp_id=emp.emp_id)

            with transaction.atomic():
                req = Requisition.objects.create(req_edd=date, req_status='PENDING', emp_id=emp_id)

                table_data = data.get('table_data', {})

                for key, value in table_data.items():
                    product_id = int(value['id'])
                    product = Product.objects.get(prod_id=product_id)
                    qty = int(value['qty'])
                    inventory = Inventory.objects.get(prod_id=product)  # Use prod_id field

                    # Get the available stock for the product from Inventory
                    available_stock = inventory.inv_qoh

                    # Determine if quantity exceeds available stock
                    exceeds_stock = qty >= available_stock

                    # Create RequisitionItem
                    requisition_item = RequisitionItem.objects.create(
                        prod_id=product, req_id=req, req_qty=qty, req_for_purchase=exceeds_stock
                    )

                    req_id = requisition_item.pk

            return JsonResponse({'message': 'Requisition added successfully', 'id': req_id})
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee does not exist'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required(login_url='user_login')
def viewpendingrequest(request, req_id):
    req = Requisition.objects.get(pk=req_id)
    req_items = RequisitionItem.objects.filter(req_id=req).select_related('prod_id')

    # Check if all req_for_purchase for this req_id is False
    show_approve_button = False
    if req_items.exists():
        req_for_purchase_count = req_items.filter(req_for_purchase=False).count()
        total_req_items_count = req_items.count()

        if req_for_purchase_count == total_req_items_count:
            show_approve_button = True

    return render(request, 'viewpendingreq.html', {
        'req_id': req,
        'req_items': req_items,
        'show_approve_button': show_approve_button  # Pass this to the template
    })

@login_required(login_url='user_login')
def delete_requisition(request, req_status, req_id):
    try:
        req = Requisition.objects.get(pk=req_id)
        req.delete()
        return redirect('/employee/requisition/'+ req_status)
    except Requisition.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')
def view_request_items(request, req_id):
    try:
        req = Requisition.objects.get(pk=req_id)
        req_items = RequisitionItem.objects.filter(req_id=req).select_related('prod_id')  # Fetch related Product data
        return render(request, 'base/requisition_items.html', {'req_id': req, 'req_items': req_items, 'nav': 'requisition'})
    except Requisition.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')
def admin_requisition_view(request, req_status):
    status = req_status.upper()
    try:
        req = Requisition.objects.filter(req_status=status)

        pending = Requisition.objects.filter(req_status='PENDING').count()
        approved = Requisition.objects.filter(req_status='APPROVED').count()
        received = Requisition.objects.filter(req_status='RECEIVED').count()

        title_case = status.title()

        context = {
            'req': req,
            'status': title_case,
            'pending': pending,
            'approved': approved,
            'received': received,
            'nav': 'requisition'
        }

        return render(request, 'base/admin_req_view.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee does not exist')

    return render(request, 'base/admin_req_view.html')

@login_required(login_url='user_login')
def view_pending_request_items(request, req_id):
    req = Requisition.objects.get(pk=req_id)
    req_items = RequisitionItem.objects.filter(req_id=req).select_related('prod_id')

    # Check if all req_for_purchase for this req_id is False
    show_approve_button = False
    if req_items.exists():
        req_for_purchase_count = req_items.filter(req_for_purchase=False).count()
        total_req_items_count = req_items.count()

        if req_for_purchase_count == total_req_items_count:
            show_approve_button = True

    return render(request, 'base/admin_req_items.html', {
        'req_id': req,
        'req_items': req_items,
        'show_approve_button': show_approve_button, 
        'nav': 'requisition'  # Pass this to the template
    })

@login_required(login_url='user_login')
# @csrf_exempt
def requisition_approval(request):
    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        comments = request.POST.get('comments')

        try:
            requisition = get_object_or_404(Requisition, req_id=req_id)

            if 'reject' in request.POST:
                requisition.req_comments = comments
                requisition.req_status = "REJECTED"
                requisition.save()
                messages.success(request, 'Requisition rejected successfully')
                return redirect(reverse('admin_requisition', kwargs={'req_status': 'pending'}))

            elif 'approved' in request.POST:  # Added leading slash
                requisition.req_status = "APPROVED"
                requisition.mark_approved()
                requisition.save()
                messages.success(request, 'Requisition approved successfully')
                return redirect('/requisition/' + req_id + '/items')

        except Requisition.DoesNotExist:
            messages.error(request, 'Requisition not found')
            return render(request, '/requisition/pending', {'nav': 'requisition'})

    else:   
        return HttpResponse('invalid_request_page')

@login_required(login_url='user_login')
@csrf_exempt
def mark_received(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        req_id = request.POST.get('req_id')
        action = request.POST.get('action')

        try:
            requisition = Requisition.objects.get(req_id=req_id)

            if action == 'receive':
                requisition.req_status = 'RECEIVED'
                requisition.mark_received()
                requisition.save()

                # Update req_item_received_qty in RequisitionItem
                requisition_items = RequisitionItem.objects.filter(req_id=requisition.req_id, req_for_purchase=False)
                for item in requisition_items:
                    item.req_item_received_qty = item.req_qty
                    item.save()

                # Update Inventory
                    update_result = update_inventory(item)
                    if not update_result:
                        # Handle scenarios where the inventory update fails
                        return JsonResponse({'success': False, 'message': 'Insufficient quantity in inventory.'})

                return JsonResponse({'success': True})

        except Requisition.DoesNotExist:
            return render(request, 'base/error.html')

        return JsonResponse({'success': False})

def update_inventory(requisition_item):
    try:
        if requisition_item.req_for_purchase == False and requisition_item.req_item_received_qty is not None:
            inventory_item = Inventory.objects.get(prod_id=requisition_item.prod_id)  # Assuming item_id is the identifier in Inventory
            received_qty = requisition_item.req_item_received_qty

            # Subtract received quantity from inv_qoh
            if inventory_item.inv_qoh >= received_qty:
                inventory_item.inv_qoh -= received_qty
                inventory_item.save()
                return True
            else:
                # Handle insufficient quantity scenario
                return False
        else:
            # For cases where req_for_purchase is True or req_item_received_qty is None
            return False

    except Inventory.DoesNotExist:
        # Handle if Inventory item doesn't exist
        return False

@login_required(login_url='user_login')    
def supplier_list(request):
    sup = Supplier.objects.all()
    context = {'sup': sup, 'nav': 'supplier'}
    return render(request, "base/supplier_lists.html", context)

@login_required(login_url='user_login')
def add_sup(request):
    try:
        if request.method == "POST":
            supplier = Supplier()
            supplier.sup_company = request.POST['sup_company'].title()
            supplier.sup_fname = request.POST['sup_fname'].title()
            supplier.sup_lname = request.POST['sup_lname'].title()
            supplier.sup_loc = request.POST['sup_loc']
            supplier.sup_mobile = request.POST['sup_mobile']
            supplier.sup_email = request.POST['sup_email']
            supplier.sup_fb_acc = request.POST['sup_fb_acc']
            supplier.save()

            sup_id = supplier.pk

            return redirect('add_contact', sup_id = sup_id)
    except IntegrityError:
        messages.error(request, 'Supplier already exist.')

    return render(request, "base/add_supplier.html", {'nav': 'supplier'})

@login_required(login_url='user_login')
def add_contact(request, sup_id):
    try:
        if request.method == "POST":
            try:
                cur_cont = Contact.objects.get(Q(sup_id=sup_id) & Q(cont_per_status='Active'))
                cur_cont.cont_per_status = 'Inactive'
                cur_cont.save()
            except:
                pass

            contact = Contact()
            contact.cont_per_fname = request.POST['cont_per_fname'].title()
            contact.cont_per_lname = request.POST['cont_per_lname'].title()
            contact.cont_per_mobile = request.POST['cont_per_mobile']
            contact.cont_per_email = request.POST['cont_per_email']
            contact.cont_per_fb_acc = request.POST['cont_per_fb_acc']
        
            sup = Supplier.objects.get(pk=sup_id)

            contact.sup_id = sup
            contact.save()

            return redirect('/supplier/' + str(sup_id) + '/details')
    except IntegrityError:
        messages.error(request, 'Contact already exist.')

    return render(request, "base/add_contact.html", {'sup_id': sup_id, 'nav': 'supplier'})

@login_required(login_url='user_login') 
def edit_contact(request, sup_id, cont_id):
    sup = Contact.objects.get(cont_per_id = cont_id)

    context={"con": sup, 'nav': 'supplier', 'sup_id': sup_id}
    return render(request, 'base/update_contact.html', context)

@login_required(login_url='user_login') 
def update_contact(request, cont_id):
    try:
        sup_id = request.POST['supmen']
        contact = Contact.objects.get(cont_per_id=cont_id)
        contact.cont_per_fname = request.POST['cont_per_fname'].title()
        contact.cont_per_lname = request.POST['cont_per_lname'].title()
        contact.cont_per_mobile = request.POST['cont_per_mobile']
        contact.cont_per_email = request.POST['cont_per_email']
        contact.cont_per_fb_acc = request.POST['cont_per_fb_acc']
        contact.save()
        id = contact.sup_id.sup_id
        context = {'emp_id': cont_id}
        return redirect('/supplier/' + str(id) + '/details')
    except IntegrityError:
        messages.error(request, 'Contact already exist.')


@login_required(login_url='user_login')
def sup_details(request, sup_id):
    try:
        contact = Contact.objects.get(Q(sup_id=sup_id) & Q(cont_per_status='Active'))
        prod = Product.objects.filter(supplier_item__sup_id=sup_id)
        sup = Supplier.objects.get(sup_id=sup_id)
        context = {'con': contact , 'prod': prod, 'sup':sup, 'nav': 'supplier'}
    
    except Contact.DoesNotExist:
        contact = Contact.objects.filter(Q(sup_id=sup_id) & Q(cont_per_status='Inactive')).count()
        prod = Product.objects.filter(supplier_item__sup_id=sup_id)
        sup = Supplier.objects.get(sup_id=sup_id)
        context = {'prod': prod, 'sup':sup, 'inact': contact, 'nav': 'supplier'}
                
    except Supplier.DoesNotExist:
        return render(request, 'base/error.html')
    
    return render(request, "base/supplier_details.html", context)

@login_required(login_url='user_login')
def deact_contact(request, cont_id):
    try:
        contact = Contact.objects.get(pk=cont_id)
        sup = contact.sup_id.sup_id
        contact.cont_per_status = 'Inactive'
        contact.save()
        return redirect('/supplier/' + str(sup) + '/details')
    except:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')
def activate_contact(request, cont_id):
    try:
        cont = Contact.objects.get(pk=cont_id)
        sup = cont.sup_id.sup_id
        try:
            cur_cont = Contact.objects.get(Q(sup_id=sup) & Q(cont_per_status='Active'))
            cur_cont.cont_per_status = 'Inactive'
            cur_cont.save()
        except:
            pass
        cont.cont_per_status = 'Active'
        cont.save()
        # return redirect('/supplier/'+ sup_id +'/details')
        return redirect(reverse('supplier_details', kwargs={'sup_id': sup}))
    except Contact.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')    
def activate_supplier(request, sup_id):
    try:
        sup = Supplier.objects.get(pk=sup_id)
        sup.sup_status = 'Active'
        sup.save()

        return redirect('supplier_list')
    except Contact.DoesNotExist:
        return render(request, 'base/error.html')
    
@login_required(login_url='user_login')
def change_contact(request, sup_id):
    try:
        past_contact = Contact.objects.filter(sup_id=sup_id, cont_per_status='Inactive')
        sup = Supplier.objects.get(pk=sup_id)

        # print(past_contact.cont_per_id)

        context = {"cont": past_contact, "sup_id": sup_id, 'nav': 'supplier'}
        return render(request, "base/change_contact.html", context)
    except Supplier.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')    
def edit_supplier(request, sup_id):
    sup = Supplier.objects.get(sup_id = sup_id)
    context={"sup": sup, 'nav': 'supplier'}
    return render(request, 'base/edit_supplier.html', context)

@login_required(login_url='user_login')
def add_sup_item(request):
    if request.method == "POST":
        sup_id = request.POST['supmen']
        prod_id = request.POST['search_id']

        try:
            # Check if Supplier_Item already exists
            supplier_item = Supplier_Item.objects.get(sup_id=sup_id, prod_id=prod_id)

        except Supplier_Item.DoesNotExist:
            # If it doesn't exist, create a new Supplier_Item
            supplier = Supplier.objects.get(sup_id=sup_id)
            product = Product.objects.get(prod_id=prod_id)

            supplier_item = Supplier_Item(sup_id=supplier, prod_id=product)
            supplier_item.save()
        # Redirect to the Supplier1 page
        return redirect('/supplier/' + sup_id + '/details')

@login_required(login_url='user_login')
def edit_profile(request):
    employee = request.user.emp
    context = {'user': request.user, 'employee': employee}
    return render(request, 'base/emp_edit_profile.html', context)

@login_required(login_url='user_login')
def change_password(request):
    if request.method == 'POST':
        employee = request.user.emp
        new_password = request.POST.get('newpass')
        confirm_password = request.POST.get('confirmpass')
        employee.emp_password = new_password

        if new_password and confirm_password and new_password == confirm_password:
            # Update user password
            request.user.set_password(new_password)
            request.user.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password updated successfully.')
        elif new_password or confirm_password:
            messages.error(request, 'Passwords do not match.')

        employee.save()
    return redirect('home')

@login_required(login_url='user_login')
def save_profile_changes(request):
    if request.method == 'POST':
        employee = request.user.emp
        employee.emp_fname = request.POST.get('firstname')
        employee.emp_lname = request.POST.get('lastname')
        employee.emp_gender = request.POST.get('gender')
        employee.emp_email = request.POST.get('email')
        employee.emp_address = request.POST.get('address')
        employee.emp_mobile = request.POST.get('mobile')
        if 'imagefile' in request.FILES:
                new_image = request.FILES['imagefile']

                if employee.emp_image:
                    # Remove the old image file before updating
                    os.remove(employee.emp_image.path)
                employee.emp_image = new_image

        employee.save()

    return redirect('home')

@login_required(login_url='user_login')
def po_list(request, po_status):
    try:
        pstat = po_status.upper()
        po = Purchase_Order.objects.filter(po_status=pstat)
        pending = Purchase_Order.objects.filter(po_status='PENDING').count()
        complete = Purchase_Order.objects.filter(po_status='COMPLETE').count()
        cancelled = Purchase_Order.objects.filter(po_status='CANCELLED').count()
        pos = RequisitionItem.objects.filter(req_for_purchase=True).values('prod_id').annotate(total_quantity=Sum('req_qty'))  #search for filtering in django #approved_requisitions = Requisition.objects.filter(req_id='Pending')
        cnt = pos.count()

        status = po_status.title()
        context = {'pos': po,
                'status': status,
                'pending': pending, 
                'complete': complete,
                'cancelled': cancelled,
                'urgent': cnt,
                'nav': 'po',
                }
        return render(request, 'base/purchase_orders.html', context)
    except:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')
def view_po(request):
    return render(request, 'base/add_po.html', {'nav': 'po'})

@login_required(login_url='user_login')
def delete_po(request, po_status, po_id):
    try:
        po = Purchase_Order.objects.get(po_id = po_id)
        po.delete()
        stat = po_status.lower()
        return redirect('/purchase/order/'+ stat +'/')
    except Purchase_Order.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')
@csrf_exempt
def search_supplier(request):
    if request.method == 'POST':
        search_id = request.POST.get('search_id')
        print('Received search_id:', search_id)
        try:
            prod = Product.objects.filter(supplier_item__sup_id=search_id)
            product_data_list = []

            # Loop through each product in the queryset
            for product in prod:
                # Add product data to the list
                product_data_list.append({
                    'Ide': product.prod_id,
                    'name': product.prod_name,
                    'brand': product.prod_brand,
                    'desc': product.prod_desc,
                    'price': product.prod_price,
                    'packsize': product.prod_pack_size,
                    # Add other fields as needed
                })

            # Return the product data as a JSON response
            return JsonResponse(product_data_list, safe=False)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)  # Handle other exceptions
    return JsonResponse({'error': 'Invalid request method'})

@login_required(login_url='user_login')
def delete_sup(request, sup_id):
    try:
        sup = Supplier.objects.get(sup_id = sup_id)
        sup.sup_status = 'Inactive'
        sup.save()
        try:
            contact = Contact.objects.get(Q(sup_id=sup_id) & Q(cont_per_status='Active'))
            contact.cont_per_status = 'Inactive'
            contact.save()
        except:
            pass
        return redirect('supplier_list')
    except Supplier.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')    
def update_supplier(request, sup_id):
    try:
        if request.method == "POST":
            supplier = Supplier.objects.get(sup_id=sup_id)  # Retrieve the existing supplier
            supplier.sup_company = request.POST['sup_company'].title()
            supplier.sup_fname = request.POST['sup_fname'].title()
            # supplier.sup_status = request.POST['status']
            supplier.sup_lname = request.POST['sup_lname'].title()
            supplier.sup_loc = request.POST['sup_loc']
            supplier.sup_mobile = request.POST['sup_mobile']
            supplier.sup_email = request.POST['sup_email']
            supplier.sup_fb_acc = request.POST['sup_fb_acc']
            supplier.save()  # Update the existing supplier

            return redirect('/supplier/' + str(sup_id) + '/details')
    except IntegrityError:
        messages.error(request, 'Supplier already exist.')
        return redirect('/supplier/list')

def delete_supplier_item(request, sup_id, prod_id):
    try:
        # prod = Product.objects.get(pk=prod_id)
        # sup = Supplier.()

        item = Supplier_Item.objects.get(Q(sup_id = sup_id) & Q(prod_id = prod_id))
        item.delete()
        return redirect('/supplier/' + str(sup_id) + '/details')
    except Supplier_Item.DoesNotExist:
        return render(request, 'base/error.html')

@login_required(login_url='user_login')
@csrf_exempt
def add_po(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            date = data.get('edd')
            sup_id = data.get('sup_id')

            # Retrieve the Supplier instance corresponding to the sup_id
            supplier = Supplier.objects.get(sup_id=sup_id)

            requisition = Requisition.objects.first()
            req_id = requisition.req_id if requisition else None

            with transaction.atomic():
                po = Purchase_Order.objects.create(
                    po_edd=date,
                    sup_id=supplier,  # Use the foreign key field
                )

                table_data = data.get('table_data', [])

                for item_data in table_data:
                    product_id = int(item_data['id'])
                    product = Product.objects.get(prod_id=product_id)
                    qty = int(item_data['qty'])

                    # Create Purchase_Order_Item
                    Purchase_Order_Item.objects.create(
                        prod_id=product,
                        po_id=po,
                        po_item_qty=qty,
                        po_item_price=product.prod_price,
                    )
            
            return JsonResponse({'message': 'Purchase Order added successfully'})
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Supplier.DoesNotExist:
            return JsonResponse({'error': 'Supplier not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required(login_url='user_login')
def view_po_items(request, po_id):
    try:
        po = Purchase_Order.objects.get(po_id=po_id)
        status = po.po_status.strip()
        sup_id = po.sup_id.sup_id
        sup = Supplier.objects.get(sup_id = sup_id)
        poitem = Purchase_Order_Item.objects.filter(po_id=po_id) 
        calculated_values = poitem.annotate(calculated_value=F('po_item_received_qty') * F('po_item_price')).values_list('calculated_value', flat=True)

    # Calculate the sum of (received_qty * price)
        total_po_item_total_complete = sum(calculated_values)
        total_po_item_total_pending = poitem.aggregate(total=Sum('po_item_total'))['total'] or 0
        context = {'poitem': poitem, 'po': po, 'sup': sup, 'total_complete': total_po_item_total_complete, 'stat': status, 'nav': 'po','calculated_values': calculated_values, 'total_pending': total_po_item_total_pending}
    except Exception as e:
        pass

    return render(request, "base/po_items.html", context)

@login_required(login_url='user_login')
def urgent_req_view(request):
    po = RequisitionItem.objects.filter(req_for_purchase=True).values('prod_id').annotate(total_quantity=Sum('req_qty'))  #search for filtering in django #approved_requisitions = Requisition.objects.filter(req_id='Pending')

    supplier = Supplier_Item.objects.all()
    prod = Product.objects.all()
    cnt = po.count()
    pending = Purchase_Order.objects.filter(po_status='PENDING').count()
    complete = Purchase_Order.objects.filter(po_status='COMPLETE').count()
    cancelled = Purchase_Order.objects.filter(po_status='CANCELLED').count()
    context = {'po': po,
               'sup' : supplier, 
               'status': 'Urgent',
               'prod': prod,
               'pending': pending, 
               'complete': complete,
               'cancelled': cancelled,
               'urgent': cnt,
               'nav': 'po'
               }
    return render(request, "base/urgent_req.html", context)

def complete_po(po_id):
    print(po_id)
    try:
        po = Purchase_Order.objects.get(po_id = po_id)
        po.po_status = 'COMPLETE'
        po.po_received_date = timezone.now()
        
        po.save()
        return True
    except:
        return False

@login_required(login_url='user_login')
def cancel_po(request, po_id):
    try:
        po = Purchase_Order.objects.get(pk=po_id)
        po.po_status = 'CANCELLED'
        po.save()
    except Purchase_Order.DoesNotExist:
        return render(request, 'base/error.html')
    
    return redirect('/purchase/order/cancelled/')

@login_required(login_url='user_login')
def confirm_po(request):
    if request.method == 'POST':
        poid = request.POST['supmen']
        received_qty_list = request.POST.getlist('rqty')

        with transaction.atomic():
            for index, received_qty in enumerate(received_qty_list):
                po_item_id = request.POST.get(f'po_item_id_{index}')
                po_item = Purchase_Order_Item.objects.get(pk=po_item_id)

                # Calculate the change in quantity
                received_qty = int(received_qty)
                old_received_qty = po_item.po_item_received_qty
                qty_change = received_qty - old_received_qty

                # Update the received_qty field
                po_item.po_item_received_qty = received_qty

                # Update the po_item_status based on your conditions
                po_item.po_item_qty = int(po_item.po_item_qty)
                if received_qty == po_item.po_item_qty:
                    po_item.po_item_status = 'COMPLETE'
                elif received_qty == 0 or received_qty is None:
                    po_item.po_item_status = 'PENDING'
                else:
                    po_item.po_item_status = 'PARTIAL'
                
                # Save the changes to the Purchase_Order_Item
                po_item.save()

                # Update the Inventory
                inventory = Inventory.objects.get(prod_id=po_item.prod_id)
                inventory.inv_qoh += qty_change
                inventory.save()
            # Update the po_status based on po_item_status values
            po_statuses = set(po_item.po_item_status for po_item in Purchase_Order_Item.objects.filter(po_id=poid))
            po = Purchase_Order.objects.get(po_id=poid)
            print(poid)
            complete_po(poid)

        # Redirect back to the page or wherever you want
        return redirect('/purchase/order/' + poid +'/items')

    # Handle the case when the request method is not POST (optional)
    return redirect('purchase/order/pending/')

def forgot_pass(request):
    return render(request, 'base/forgot_pass.html')

def custom_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('emailaddress')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return render(request, 'base/forgot_pass.html')

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = f"http://{request.get_host()}/reset/{uidb64}/{token}/"

        send_mail(
            'Password Reset',
            f'Click the following link to reset your password: {reset_url}',
            'ICC_Chrishna@gmail.com',
            [email],
            fail_silently=False,
        )

        # Display SweetAlert notification on success
        success_message = "Password reset instructions sent to your email. Check your inbox (and spam folder)."
        return render(request, 'base/forgot_pass.html', {'success_message': success_message})

    return HttpResponseBadRequest("Invalid request.")

def password_reset_confirm(request, uidb64, token):
    if request.method == 'POST':
        # Decode the UID to get the user ID
        user_id = int(urlsafe_base64_decode(uidb64).decode('utf-8'))

        # Get the user object based on the user ID
        user = CustomUser.objects.get(id=user_id)
        
        newpass = request.POST.get('newpassword')
        confirmpass = request.POST.get('confirmpassword')
        
        if newpass == confirmpass:
            # Check if the token is valid
            if default_token_generator.check_token(user, token):
                employee = user.emp
                employee.emp_password = newpass
                employee.save()
                user.set_password(newpass)
                user.save()
                return redirect(user_login)
            else:
                return render(request, 'base/forgot_pass_change.html', {'uidb64': uidb64, 'token': token})
        else:
            return render(request, 'base/forgot_pass_change.html', {'uidb64': uidb64, 'token': token})
    return render(request, 'base/forgot_pass_change.html', {'uidb64': uidb64, 'token': token})