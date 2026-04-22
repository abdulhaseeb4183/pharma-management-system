from django.contrib import admin
from .models import *

# Saari 40 Tables ki list
models_list = [
    # Setup
    Country, City, Currency, UnitOfMeasure, Department, Designation, Bank, TaxCategory,
    # HR
    Employee, EmployeeAttendance, LeaveRequest, Payroll, ShiftSchedule,
    # Supply Chain
    SupplierCategory, Supplier, RawMaterialCategory, RawMaterial, PurchaseOrder, PurchaseOrderItem,
    # Production
    MedicineType, MedicineCategory, Medicine, Formula, FormulaItem, Machine, ProductionBatch, ProductionLog,
    # Inventory
    Warehouse, Rack, Stock, StockAdjustment,
    # Quality Control
    TestParameter, QCInspection, QCResult,
    # Sales
    CustomerCategory, Customer, SalesOrder, SalesOrderItem, SalesInvoice, SalesReturn
]

# Ek loop ke zariye sabko register kar rahe hain
for model in models_list:
    admin.site.register(model)