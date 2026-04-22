from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, RegexValidator

# --- GLOBAL VALIDATORS ---
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

# ==========================================
# MODULE 1: GENERAL SETUP & MASTER DATA (Tables 1-8)
# ==========================================

# Table 1: Country
class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5, help_text="e.g., PK, US")

    def __str__(self):
        return self.name

# Table 2: City (Linked to Country)
class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Table 3: Currency (For Import/Export rates)
class Currency(models.Model):
    name = models.CharField(max_length=50, help_text="e.g., Pakistani Rupee")
    symbol = models.CharField(max_length=10, help_text="e.g., PKR, $")
    exchange_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1.00,
        validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return self.symbol

# Table 4: Unit of Measure (KG, Litre, Box for medicines)
class UnitOfMeasure(models.Model):
    name = models.CharField(max_length=50, help_text="e.g., Kilogram, Tablet, Box")
    short_code = models.CharField(max_length=10, help_text="e.g., kg, tab")

    def __str__(self):
        return self.name

# Table 5: Department (Production, Sales, HR)
class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# Table 6: Designation (Manager, Worker, Pharmacist)
class Designation(models.Model):
    title = models.CharField(max_length=100)
    level = models.IntegerField(
        help_text="1 for Junior, 10 for Senior",
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return self.title

# Table 7: Bank (Company Bank Accounts)
class Bank(models.Model):
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    branch_code = models.CharField(max_length=20)
    balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

# Table 8: Tax Category (GST, WHT)
class TaxCategory(models.Model):
    name = models.CharField(max_length=50, help_text="e.g., GST 18%")
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0.00)]
    )

    def __str__(self):
        return self.name

# ==========================================
# MODULE 2: HUMAN RESOURCES (HR) (Tables 9-10)
# ==========================================

# Table 9: Employee
class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, validators=[phone_validator])
    date_joined = models.DateField(default=timezone.now)
    basic_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.00)]
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Table 10: Employee Attendance
class EmployeeAttendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time_in = models.TimeField()
    time_out = models.TimeField(null=True, blank=True)
    is_present = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.employee} - {self.date}"

# ==========================================
# MODULE 2: HUMAN RESOURCES (HR) - Continued (Tables 11-13)
# ==========================================

# Table 11: Leave Request (Chutti ki darkhwast)
class LeaveRequest(models.Model):
    LEAVE_TYPES = [('Sick', 'Sick'), ('Casual', 'Casual'), ('Annual', 'Annual')]
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.employee} - {self.leave_type}"

# Table 12: Payroll (Salary Slips)
class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.DateField(help_text="Select any date of the month")
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payroll: {self.employee} - {self.month}"

# Table 13: Shift Schedule (Morning/Night Shifts)
class ShiftSchedule(models.Model):
    name = models.CharField(max_length=50, help_text="e.g., Morning Shift A")
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name


# ==========================================
# MODULE 3: SUPPLY CHAIN & RAW MATERIAL (Tables 14-19)
# ==========================================

# Table 14: Supplier Category (Local vs International)
class SupplierCategory(models.Model):
    name = models.CharField(max_length=50, help_text="e.g., Local Distributor, International Importer")

    def __str__(self):
        return self.name

# Table 15: Supplier (Jahan se samaan aata hai)
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(SupplierCategory, on_delete=models.SET_NULL, null=True)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, validators=[phone_validator])
    email = models.EmailField()
    address = models.TextField()
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

# Table 16: Raw Material Category (Active API vs Excipients/Packaging)
class RawMaterialCategory(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., Active Pharmaceutical Ingredient (API)")
    
    def __str__(self):
        return self.name

# Table 17: Raw Material (Chemicals Definition)
class RawMaterial(models.Model):
    name = models.CharField(max_length=200, help_text="Chemical Name")
    category = models.ForeignKey(RawMaterialCategory, on_delete=models.CASCADE)
    unit = models.ForeignKey(UnitOfMeasure, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    reorder_level = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Alert when stock is below this",
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return self.name

# Table 18: Purchase Order (Supplier ko order dena)
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [('Draft', 'Draft'), ('Sent', 'Sent'), ('Received', 'Received')]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_date = models.DateField(default=timezone.now)
    expected_delivery = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    total_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )

    def __str__(self):
        return f"PO-{self.id} : {self.supplier}"

# Table 19: Purchase Order Items (Order ke andar items)
class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    total_price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.00)])

    def __str__(self):
        return f"{self.raw_material.name} ({self.quantity})"

# ==========================================
# MODULE 4: PRODUCTION (Start) (Table 20)
# ==========================================

# Table 20: Medicine Type (Form)
class MedicineType(models.Model):
    name = models.CharField(max_length=50, help_text="e.g., Tablet, Capsule, Syrup, Injection")

    def __str__(self):
        return self.name

# ==========================================
# MODULE 4: PRODUCTION & MANUFACTURING - Continued (Tables 21-27)
# ==========================================

# Table 21: Medicine Category (Therapeutic Class)
class MedicineCategory(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., Antibiotic, Painkiller, Anti-Viral")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# Table 22: Medicine (Main Product Definition)
class Medicine(models.Model):
    name = models.CharField(max_length=200, help_text="Brand Name e.g., Panadol")
    generic_name = models.CharField(max_length=200, help_text="Chemical Name e.g., Paracetamol")
    type = models.ForeignKey(MedicineType, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(MedicineCategory, on_delete=models.SET_NULL, null=True)
    shelf_life_months = models.IntegerField(
        help_text="Expiry period in months",
        validators=[MinValueValidator(1)]
    )
    sale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.00)]
    )
    manufacturing_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )

    def __str__(self):
        return f"{self.name} ({self.generic_name})"

# Table 23: Formula / Master Recipe (Kis dawa me kya dalega)
class Formula(models.Model):
    medicine = models.OneToOneField(Medicine, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Formula for {self.medicine.name}"

# Table 24: Formula Items (Recipe Ingredients)
class FormulaItem(models.Model):
    formula = models.ForeignKey(Formula, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity_required = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        help_text="Quantity for 1 unit of medicine",
        validators=[MinValueValidator(0.0001)]
    )

    def __str__(self):
        return f"{self.raw_material.name} for {self.formula.medicine.name}"

# Table 25: Machine (Production Equipment)
class Machine(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., Mixer A, Tablet Press 1")
    model_number = models.CharField(max_length=50)
    purchase_date = models.DateField()
    last_maintenance_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

# Table 26: Production Batch (Most Important Table)
class ProductionBatch(models.Model):
    STAGES = [('Planning', 'Planning'), ('Mixing', 'Mixing'), ('Packaging', 'Packaging'), ('QC', 'QC Pending'), ('Completed', 'Completed')]
    
    batch_number = models.CharField(max_length=50, unique=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity_to_produce = models.IntegerField(validators=[MinValueValidator(1)])
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    mfg_date = models.DateField()
    exp_date = models.DateField()
    current_stage = models.CharField(max_length=20, choices=STAGES, default='Planning')

    def __str__(self):
        return f"Batch {self.batch_number} - {self.medicine.name}"

# Table 27: Production Log (Daily Output Tracking)
class ProductionLog(models.Model):
    batch = models.ForeignKey(ProductionBatch, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL, null=True)
    quantity_produced = models.IntegerField(validators=[MinValueValidator(0)])
    damaged_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    operator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.batch.batch_number} - {self.date}"


# ==========================================
# MODULE 5: INVENTORY & WAREHOUSING (Tables 28-30)
# ==========================================

# Table 28: Warehouse (Store Locations)
class Warehouse(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., Central Warehouse, Cold Storage")
    address = models.TextField()
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

# Table 29: Rack / Shelf (Location inside Warehouse)
class Rack(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    rack_number = models.CharField(max_length=20, help_text="e.g., Row A - Shelf 1")

    def __str__(self):
        return f"{self.warehouse.name} - {self.rack_number}"

# Table 30: Stock (Live Inventory Status)
class Stock(models.Model):
    # This table can hold EITHER Raw Material OR Medicine
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    
    # Generic Relations or simple nullable Foreign Keys (Simple way used here)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, null=True, blank=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, null=True, blank=True)
    batch = models.ForeignKey(ProductionBatch, on_delete=models.SET_NULL, null=True, blank=True) # Only for medicines
    
    quantity = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        item = self.medicine.name if self.medicine else (self.raw_material.name if self.raw_material else "Unknown")
        return f"{item} : {self.quantity}"

# ==========================================
# MODULE 5: INVENTORY - Continued (Table 31)
# ==========================================

# Table 31: Stock Adjustment (Agar stock count mein ghalti ho ya expiry ho)
class StockAdjustment(models.Model):
    ADJUSTMENT_TYPES = [('Damage', 'Damaged/Expired'), ('Correction', 'Count Correction'), ('Gift', 'Promotional Gift')]
    
    date = models.DateField(default=timezone.now)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    # Generic relation to item
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, null=True, blank=True)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, null=True, blank=True)
    
    quantity_adjusted = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Negative for reduction, Positive for addition"
        # No validator here because reduction can be negative
    )
    reason = models.TextField()
    type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    adjusted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Adj: {self.date} - {self.type}"


# ==========================================
# MODULE 6: QUALITY CONTROL (QC) (Tables 32-34)
# ==========================================

# Table 32: Test Parameter (Kya check karna hai?)
class TestParameter(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., pH Level, Hardness, Dissolution Time")
    unit = models.CharField(max_length=20, blank=True, help_text="e.g., pH, min, kg")
    standard_min = models.DecimalField(max_digits=10, decimal_places=2, help_text="Minimum acceptable value")
    standard_max = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum acceptable value")

    def __str__(self):
        return f"{self.name} ({self.standard_min} - {self.standard_max})"

# Table 33: QC Inspection (Testing Event)
class QCInspection(models.Model):
    batch = models.ForeignKey(ProductionBatch, on_delete=models.CASCADE)
    inspection_date = models.DateField(default=timezone.now)
    inspector = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    overall_status = models.CharField(max_length=20, choices=[('Pass', 'Pass'), ('Fail', 'Fail')], default='Fail')
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"QC: {self.batch.batch_number} - {self.overall_status}"

# Table 34: QC Result (Detailed Results)
class QCResult(models.Model):
    inspection = models.ForeignKey(QCInspection, on_delete=models.CASCADE)
    parameter = models.ForeignKey(TestParameter, on_delete=models.CASCADE)
    observed_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_pass = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.parameter.name}: {self.observed_value} ({'Pass' if self.is_pass else 'Fail'})"


# ==========================================
# MODULE 7: SALES & DISTRIBUTION (Tables 35-40)
# ==========================================

# Table 35: Customer Category
class CustomerCategory(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., Distributor, Retail Pharmacy, Hospital")
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )

    def __str__(self):
        return self.name

# Table 36: Customer (Clients)
class Customer(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(CustomerCategory, on_delete=models.SET_NULL, null=True)
    license_number = models.CharField(max_length=50, help_text="Medical Store/Pharma License No")
    phone = models.CharField(max_length=20, validators=[phone_validator])
    email = models.EmailField(blank=True)
    area = models.CharField(max_length=100)
    credit_limit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=50000.00,
        validators=[MinValueValidator(0.00)]
    )

    def __str__(self):
        return self.name

# Table 37: Sales Order (Booking)
class SalesOrder(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Shipped', 'Shipped'), ('Cancelled', 'Cancelled')]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    sales_rep = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, help_text="Salesman")
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )

    def __str__(self):
        return f"SO-{self.id} : {self.customer.name}"

# Table 38: Sales Order Item (Line Items)
class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    total_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.00)])

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

# Table 39: Sales Invoice (Final Bill)
class SalesInvoice(models.Model):
    sales_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"INV-{self.id} for SO-{self.sales_order.id}"

# Table 40: Sales Return (Wapas aaya maal)
class SalesReturn(models.Model):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    reason = models.TextField(help_text="e.g., Expired, Damaged in transit")
    date_returned = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Return: {self.medicine.name} from INV-{self.invoice.id}"