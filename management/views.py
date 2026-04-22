from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, ForeignKey
from django.db.models.functions import TruncMonth
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from django.apps import apps  # Model dhundne ke liye
from django.contrib import messages # Messages ke liye
from django.forms import modelform_factory # Automatic form ke liye
from django.http import HttpResponse # Popup close script ke liye
from django.utils.html import escapejs # Javascript safe text ke liye

from .models import *
from .forms import UserLoginForm, UserRegisterForm

# --- 1. PUBLIC HOME PAGE VIEW ---
def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

# --- 2. AUTHENTICATION VIEWS ---
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# --- HELPER FUNCTIONS ---
def get_last_6_months():
    months = []
    today = datetime.today()
    for i in range(5, -1, -1):
        d = today - timedelta(days=i*30)
        months.append(d.strftime("%b"))
    return months

def get_revenue_trend():
    data = []
    today = datetime.today()
    for i in range(5, -1, -1):
        start_date = today - timedelta(days=(i+1)*30)
        end_date = today - timedelta(days=i*30)
        val = SalesOrder.objects.filter(
            date__gte=start_date, 
            date__lte=end_date
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        data.append(int(val))
    return data

# --- 3. MAIN DASHBOARD VIEW ---
@login_required(login_url='login')
def dashboard(request):
    total_medicines = Medicine.objects.count()
    total_orders = SalesOrder.objects.count()
    low_stock = Stock.objects.filter(quantity__lt=50).count()
    revenue_data = SalesOrder.objects.aggregate(Sum('total_amount'))
    total_revenue = revenue_data['total_amount__sum'] or 0

    med_types = Medicine.objects.values('type__name').annotate(count=Count('id'))
    med_labels = [m['type__name'] for m in med_types] if med_types else ['No Data']
    med_data = [m['count'] for m in med_types] if med_types else [0]

    qc_pass = QCInspection.objects.filter(overall_status='Pass').count()
    qc_fail = QCInspection.objects.filter(overall_status='Fail').count()

    graph_revenue_labels = get_last_6_months()
    graph_revenue_data = get_revenue_trend()

    pending_orders = SalesOrder.objects.filter(status='Pending').count()
    completed_orders = SalesOrder.objects.filter(status__in=['Shipped', 'Delivered']).count()

    in_stock = Stock.objects.filter(quantity__gte=50).count()
    expired = 0 

    dept_counts = Employee.objects.values('department__name').annotate(count=Count('id'))
    dept_labels = [entry['department__name'] for entry in dept_counts] if dept_counts else ['No Staff']
    dept_data = [entry['count'] for entry in dept_counts] if dept_counts else [0]

    recent_invoices = SalesInvoice.objects.select_related('sales_order__customer').order_by('-id')[:5]

    context = {
        'total_medicines': total_medicines,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'low_stock': low_stock,
        'med_labels': med_labels, 'med_data': med_data,
        'qc_data': [qc_pass, qc_fail],
        'rev_labels': graph_revenue_labels, 'rev_data': graph_revenue_data,
        'order_data': [pending_orders, completed_orders],
        'inv_data': [in_stock, low_stock, expired],
        'hr_labels': dept_labels, 'hr_data': dept_data,
        'recent_invoices': recent_invoices,
    }
    return render(request, 'dashboard.html', context)

# --- 4. DEPARTMENT: SALES ---
@login_required(login_url='login')
def dept_sales(request):
    rev = SalesOrder.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    orders = SalesOrder.objects.count()
    cust = Customer.objects.count()
    pending = SalesOrder.objects.filter(status='Pending').count()
    
    table = SalesOrder.objects.select_related('customer').order_by('-id')[:10]
    
    graph_labels = get_last_6_months()
    graph_data = get_revenue_trend()

    context = {
        'dept_name': 'Sales & Distribution',
        'stat1_label': 'Total Revenue', 'stat1_value': f"Rs. {rev}", 'stat1_icon': 'fa-wallet', 'stat1_color': 'success',
        'stat2_label': 'Total Orders', 'stat2_value': orders, 'stat2_icon': 'fa-shopping-cart', 'stat2_color': 'primary',
        'stat3_label': 'Customers', 'stat3_value': cust, 'stat3_icon': 'fa-users', 'stat3_color': 'info',
        'stat4_label': 'Pending', 'stat4_value': pending, 'stat4_icon': 'fa-clock', 'stat4_color': 'warning',
        'table_rows': table,
        'graph_labels': graph_labels,
        'graph_data': graph_data,
    }
    return render(request, 'department_details.html', context)

# --- 5. DEPARTMENT: HR ---
@login_required(login_url='login')
def dept_hr(request):
    emp = Employee.objects.count()
    try:
        present = EmployeeAttendance.objects.filter(date=datetime.today().date(), is_present=True).count() 
    except:
        present = 0
    
    payroll = Payroll.objects.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
    leaves = LeaveRequest.objects.filter(status='Pending').count()
    
    table = Employee.objects.all().order_by('-id')[:10]
    
    d_counts = Employee.objects.values('department__name').annotate(count=Count('id'))
    g_labels = [e['department__name'] for e in d_counts]
    g_data = [e['count'] for e in d_counts]

    context = {
        'dept_name': 'HR & Payroll',
        'stat1_label': 'Total Staff', 'stat1_value': emp, 'stat1_icon': 'fa-user-tie', 'stat1_color': 'primary',
        'stat2_label': 'Present Today', 'stat2_value': present, 'stat2_icon': 'fa-check-circle', 'stat2_color': 'success',
        'stat3_label': 'Payroll', 'stat3_value': f"Rs. {payroll}", 'stat3_icon': 'fa-money-bill', 'stat3_color': 'danger',
        'stat4_label': 'Leaves', 'stat4_value': leaves, 'stat4_icon': 'fa-envelope', 'stat4_color': 'warning',
        'table_rows': table,
        'graph_labels': g_labels,
        'graph_data': g_data,
    }
    return render(request, 'department_details.html', context)

# --- 6. DEPARTMENT: INVENTORY ---
@login_required(login_url='login')
def dept_inventory(request):
    meds = Medicine.objects.count()
    low = Stock.objects.filter(quantity__lt=50).count()
    stock_val = 0 
    expired = 0

    table = Medicine.objects.all().order_by('-id')[:10]

    m_types = Medicine.objects.values('type__name').annotate(count=Count('id'))
    g_labels = [m['type__name'] for m in m_types]
    g_data = [m['count'] for m in m_types]

    context = {
        'dept_name': 'Inventory & Store',
        'stat1_label': 'Medicines', 'stat1_value': meds, 'stat1_icon': 'fa-pills', 'stat1_color': 'info',
        'stat2_label': 'Low Stock', 'stat2_value': low, 'stat2_icon': 'fa-exclamation-triangle', 'stat2_color': 'danger',
        'stat3_label': 'Stock Value', 'stat3_value': f"Rs. {stock_val}", 'stat3_icon': 'fa-boxes', 'stat3_color': 'success',
        'stat4_label': 'Expired', 'stat4_value': expired, 'stat4_icon': 'fa-trash', 'stat4_color': 'secondary',
        'table_rows': table,
        'graph_labels': g_labels,
        'graph_data': g_data,
    }
    return render(request, 'department_details.html', context)

# ==========================================
#  MANUAL CRUD OPERATIONS
# ==========================================

# 1. DELETE RECORD
@login_required(login_url='login')
def delete_record(request, model_name, record_id):
    try:
        model = apps.get_model('management', model_name)
        record = get_object_or_404(model, id=record_id)
        record.delete()
        messages.success(request, f"{model_name} deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting record: {e}")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

# 2. ADD / EDIT RECORD (With Fixed + Button Logic)
@login_required(login_url='login')
def save_record(request, model_name, record_id=None):
    try:
        model = apps.get_model('management', model_name)
    except LookupError:
        return HttpResponse("Model not found", status=404)

    FormClass = modelform_factory(model, exclude=[])

    if record_id:
        instance = get_object_or_404(model, id=record_id)
        form = FormClass(request.POST or None, instance=instance)
        title = f"Edit {model_name}"
    else:
        form = FormClass(request.POST or None)
        title = f"Add New {model_name}"

    # --- LOGIC: Foreign Key Fields par '+' Button Lagana ---
    for field in model._meta.get_fields():
        if isinstance(field, ForeignKey) and field.name in form.fields:
            related_model = field.related_model.__name__
            field_id = f"id_{field.name}" 
            # FIXED: Used underscore (_) instead of hyphen (-) to prevent TemplateError
            form.fields[field.name].widget.attrs['data_add_url'] = f"/add/{related_model}/?_field={field_id}"

    if request.method == 'POST':
        if form.is_valid():
            saved_instance = form.save()
            
            # --- Check: Kya ye Child Window thi? ---
            target_field = request.GET.get('_field')
            
            if target_field:
                new_id = saved_instance.pk
                new_name = escapejs(str(saved_instance))
                
                return HttpResponse(f'''
                    <script>
                        window.opener.updateRelatedField('{target_field}', '{new_id}', '{new_name}');
                        window.close();
                    </script>
                ''')
            else:
                return HttpResponse('<script>window.parent.location.reload();</script>')

    return render(request, 'universal_form.html', {'form': form, 'title': title})