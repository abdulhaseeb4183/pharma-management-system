from django.contrib import admin
from django.urls import path
from management import views  # Ensure views are imported correctly

urlpatterns = [
    # --- 1. DJANGO ADMIN (Backup) ---
    path('admin/', admin.site.urls),

    # --- 2. PUBLIC LANDING PAGE (Root URL) ---
    # Jab koi website kholega to Home page dikhega
    path('', views.home_view, name='home'),

    # --- 3. AUTHENTICATION ---
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # --- 4. MAIN DASHBOARD (Protected) ---
    # Login ke baad user yahan redirect hoga
    path('dashboard/', views.dashboard, name='dashboard'),

    # --- 5. DEPARTMENT DASHBOARDS ---
    path('dashboard/sales/', views.dept_sales, name='dept_sales'),
    path('dashboard/hr/', views.dept_hr, name='dept_hr'),
    path('dashboard/inventory/', views.dept_inventory, name='dept_inventory'),

    # --- 6. MANUAL CRUD OPERATIONS (Universal Views) ---
    
    # ADD New Record (Create) - Example: /add/SalesOrder/
    path('add/<str:model_name>/', views.save_record, name='add_record'),
    
    # EDIT Existing Record (Update) - Example: /edit/SalesOrder/5/
    path('edit/<str:model_name>/<int:record_id>/', views.save_record, name='edit_record'),

    # DELETE Record - Example: /delete/SalesOrder/5/
    path('delete/<str:model_name>/<int:record_id>/', views.delete_record, name='delete_record'),
]