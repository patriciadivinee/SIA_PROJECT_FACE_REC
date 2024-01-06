from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils import timezone

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('emp_access', True)


        return self.create_user(email, password, **extra_fields)

# Create your models here.
class Employee(models.Model):
    emp_id = models.BigAutoField(primary_key=True, editable=False)
    emp_fname = models.CharField(max_length=50)
    emp_lname = models.CharField(max_length=50)
    emp_gender = models.CharField(max_length=6)
    emp_mobile = models.CharField(max_length=11)
    emp_dob = models.DateField()
    emp_address = models.CharField(max_length=255)
    emp_email = models.EmailField(unique=True)
    emp_password = models.CharField(max_length=20)
    emp_image = models.ImageField(upload_to="uploads/", null=True, blank=True)
    emp_status = models.BooleanField(default=True)
    emp_created_at = models.DateField(auto_now_add=True)
    emp_updated_at = models.DateField(auto_now = True)

    class Meta:
        db_table = 'employee'
        unique_together = ('emp_fname', 'emp_lname', 'emp_dob')

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    emp = models.OneToOneField(Employee, null=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    emp_access = models.BooleanField(default=False)

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email

class Category(models.Model):
    cat_id = models.BigAutoField(primary_key=True, editable=False)
    cat_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.cat_name
    
    class Meta:
        db_table = 'category'

class Product(models.Model):
    prod_id = models.BigAutoField(primary_key=True, editable=False)
    prod_brand = models.CharField(max_length=50, null=False)
    prod_name = models.CharField(max_length=50, null=False)
    prod_desc = models.CharField(max_length=255, null=False)
    prod_price = models.DecimalField(max_digits=9, decimal_places=2, null=False)
    prod_pack_size = models.CharField(max_length=10, null=False)
    prod_status = models.CharField(max_length=15, default='Upcoming')
    cat_id = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, db_column='cat_id')

    class Meta:
        db_table = 'product'
        # models.UniqueConstraint(fields=['prod_name', 'prod_pack_size'], name='unique_name_size')
        unique_together = ['prod_brand', 'prod_name', 'prod_pack_size']
    
class Inventory(models.Model):
    prod_id = models.OneToOneField(Product, primary_key=True, on_delete=models.CASCADE, editable=False, db_column='prod_id')
    inv_qoh = models.IntegerField(null=False)
    inv_status = models.CharField(max_length=15, null=False, default='In Stock')
    inv_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory'

class Requisition(models.Model):
    req_id = models.BigAutoField(primary_key=True, editable=False)
    req_edd = models.DateField(null=True)
    req_status = models.CharField(max_length=10, null=False)
    req_comments = models.CharField(max_length=255)
    req_received_date = models.DateTimeField(null=True, blank=True)
    req_approved_date = models.DateTimeField(null=True, blank=True)
    req_created_at = models.DateTimeField(auto_now_add=True)
    emp_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, db_column='emp_id')

    class Meta:
        db_table = 'requisition'

    def __str__(self):
        return str(self.req_id)  # Convert req_id to string for representation

    def mark_received(self):
        self.req_status = 'RECEIVED'
        self.req_received_date = timezone.now()  # Set received date

    def mark_approved(self):
        self.req_status = 'APPROVED'
        self.req_approved_date = timezone.now()  # Set approved date

class RequisitionItem(models.Model):
    req_item_id = models.BigAutoField(primary_key=True, editable=False)
    req_qty = models.IntegerField(null=False)
    req_item_received_qty=models.IntegerField(null=True)
    req_for_purchase = models.BooleanField(default=False)
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, db_column='prod_id')
    req_id = models.ForeignKey(Requisition, on_delete=models.CASCADE, null=False, db_column='req_id')

    class Meta:
        db_table = 'requisition_item'
        unique_together = ['req_id', 'prod_id']

class Supplier(models.Model):
    sup_id = models.AutoField(primary_key=True, editable=False)
    sup_company = models.CharField(max_length=30, unique=True)
    sup_fname = models.CharField(max_length=30)
    sup_mname = models.CharField(max_length=30, blank=True)
    sup_lname = models.CharField(max_length=30)
    sup_loc = models.CharField(max_length=50)
    sup_mobile =models.CharField(max_length=11, unique=True)
    sup_email = models.CharField(max_length=30, unique=True)
    sup_fb_acc= models.URLField(max_length=150, unique=True)
    sup_status = models.CharField(max_length=10, null=False, default='Active')

    class Meta:
        db_table = 'supplier'

class Contact(models.Model):
    cont_per_id = models.AutoField(primary_key=True, editable=False)
    cont_per_fname = models.CharField(max_length=30)
    cont_per_lname = models.CharField(max_length=30)
    cont_per_mobile =models.CharField(max_length=11, unique=True)
    cont_per_email = models.CharField(max_length=30, unique=True)
    cont_per_fb_acc= models.URLField(max_length=150, unique=True)
    sup_id = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=False, db_column='sup_id')
    cont_per_status = models.CharField(max_length=10, null=False, default='Active')

    class Meta:
         db_table = 'contact_person'
         unique_together = ['cont_per_fname', 'cont_per_lname']

class Supplier_Item(models.Model):
    supit_id = models.BigAutoField(primary_key=True, editable=False)
    sup_id = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=False, db_column='sup_id')
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, db_column='prod_id')

    class Meta:
         db_table = 'supplier_item'
         unique_together = ['sup_id', 'prod_id']

class Purchase_Order(models.Model):
    po_id = models.BigAutoField(primary_key=True, editable=False)
    po_edd = models.DateField(null=True)
    po_status = models.CharField(max_length=10, null=False, default='PENDING')
    po_received_date = models.DateTimeField(null=True, blank=True)
    po_created_at = models.DateTimeField(auto_now_add=True)
    sup_id = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=False, db_column='sup_id')

    class Meta:
        db_table = 'purchase_order'

class Purchase_Order_Item(models.Model):
    po_item_id = models.BigAutoField(primary_key=True, editable=False)
    po_item_qty = models.IntegerField(null=False)
    po_item_received_qty = models.IntegerField(null=True,default=0)
    po_item_price = models.DecimalField(max_digits=9, decimal_places=2, null=False)
    po_item_total = models.DecimalField(max_digits=9, decimal_places=2, null=False)
    po_item_status = models.CharField(max_length=10, null=False, default='PENDING')
    po_id = models.ForeignKey(Purchase_Order, on_delete=models.CASCADE, null=False, db_column='po_id')
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, db_column='prod_id')

    class Meta:
        db_table = 'purchase_order_item'
        unique_together = ['po_id', 'prod_id']

    def save(self, *args, **kwargs):
        # Calculate po_item_total before saving
        self.po_item_total = self.po_item_qty * self.po_item_price

        # Check if po_item_status is changed to 'PARTIAL'
        if self.po_item_status == 'PARTIAL':
            self.po_item_total = self.po_item_received_qty * self.po_item_price

        super().save(*args, **kwargs)