# Copyright (c) 2022, Jide Olayinka and contributors
# For license information, please see license.txt

import frappe
# from frappe import _

def execute(filters=None):
    columns, data = [], []
    condition_date, condition_employee, condition_department = "", "", ""
    
    if filters.date_from_filter and filters.date_to_filter:
        if filters.date_from_filter == None:
            filters.date_from_filter = frappe.datetime.get_today()
        if filters.date_to_filter == None:
            filters.date_to_filter = frappe.datetime.get_today()
        condition_date = "AND wd.log_date BETWEEN '"+ filters.date_from_filter + \
            "' AND '" + filters.date_to_filter + "'"
    
    if filters.get("employee_id"):
        empid = filters.get("employee_id")
        condition_employee += f" AND wd.employee = '{empid}'"
    
    if filters.get("department"):
        department = filters.get("department")
        condition_department += f" AND emp.department = '{department}'"

    employees = frappe.db.get_list('Employee', pluck='name')
    employee_list = ','.join(employees)
    print(employee_list)
    columns = [        
        {'fieldname':'employee','label':'Employee','width':250, 'fieldtype':'Link', 'options': 'Employee'},
        # {'fieldname':'employee_name','label':'Employee Name','width':160},
        {'fieldname':'total_work_seconds','label':'Arbeitsstunden', "width": 150},
        {'fieldname':'expected_break_hours','label':'Erwartete Pausenzeit','width':150},
        {'fieldname':'actual_working_seconds','label':'Arbeitsstunden - Pause', "width": 150},
        {'fieldname':'total_target_seconds','label':'Erwartete Arbeitsstunden','width':150},
        # {'fieldname':'diff_log','label':'Erwartete Arbeitsstunden Differenz (Work Hours - Target Seconds)','width':150},
        {'fieldname':'actual_diff_log','label':'Tatsächliche Differenz (Actual Working Hours - Target Seconds)','width':150},
        {'fieldname':'total_actual_diff_log','label':'Stundenkonto (Actual Working Hours - Target Seconds)','width':150},
        # {'fieldname':'total_first_in','label':'First Checkin','width':100},
        # {'fieldname':'total_last_out','label':'Last Checkout','width':100},
        # {'fieldname':'total_attendance','label':'Total Attendance','width': 160},
        {'fieldname':'flexitime_correction','label':'Korrektur','width':120},
    ]

    work_data = frappe.db.sql(
        f"""        
        SELECT wd.employee, emp.employee_name,
            SUM(wd.total_work_seconds) as total_work_seconds,
            SUM(wd.expected_break_hours*60*60) as expected_break_hours,
            SUM(IFNULL(wd.actual_working_hours,0)*60*60) as actual_working_seconds,
            SUM(wd.total_target_seconds) as total_target_seconds,
            SUM((wd.total_work_seconds - wd.total_target_seconds)) as diff_log,
            SUM((wd.actual_working_hours*60*60 - wd.total_target_seconds)) as actual_diff_log,
            SUM((wd.actual_working_hours*60*60 - wd.total_target_seconds)) + IFNULL(fc.flexitime_correction,0) as total_actual_diff_log,
            IFNULL(fc.flexitime_correction,0) as flexitime_correction
        FROM `tabWorkday` wd
        LEFT JOIN `tabEmployee` emp ON wd.employee = emp.name
        LEFT JOIN (
            SELECT employee,
                SUM(correction*60*60) as flexitime_correction
            FROM `tabFlexitimeCorrection`
            GROUP BY employee
        ) fc ON wd.employee = fc.employee
        # LEFT JOIN `tabFlexitimeCorrection` fc ON wd.employee = fc.employee AND wd.log_date = fc.date
        WHERE wd.docstatus < 2 {condition_date} {condition_employee} {condition_department}
        GROUP BY wd.employee
        """, as_dict=1,
    )
    # wd.employee in ({employee_list}) AND 
    data = work_data

    return columns, data
