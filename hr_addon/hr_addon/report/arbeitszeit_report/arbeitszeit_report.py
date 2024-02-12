# Copyright (c) 2022, Jide Olayinka and contributors
# For license information, please see license.txt

import frappe
from frappe import _

# Function to get the employee ID of the current logged-in user
def get_employee_id():
		# Get the current user
		current_user = frappe.session.user

		# Fetch the user document
		user_doc = frappe.get_doc("Employee", {"user_id": current_user})

		# Check if the user document exists
		if user_doc:
				# Retrieve the employee ID from the user document
				employee_id = user_doc.employee

				# Print or use the employee ID as needed
				print(f"The employee ID of {current_user} is: {employee_id}")
				return employee_id
		else:
				print(f"User document not found for {current_user}")
				return None

def execute(filters=None):
	columns, data = [], []
	condition_date,condition_employee = "",""
	if filters.date_from_filter and filters.date_to_filter :
		if filters.date_from_filter == None:
			filters.date_from_filter = frappe.datetime.get_today()
		if filters.date_to_filter == None:
			filters.date_to_filter = frappe.datetime.get_today()
		condition_date = "AND log_date BETWEEN '"+ filters.date_from_filter + \
				"' AND '" + filters.date_to_filter + "'"

	employee_id = get_employee_id()
	condition_employee += f" AND wd.employee = '{employee_id}'"

	# if filters.get("employee_id"):
		# empid = filters.get("employee_id")
		# condition_employee += f" AND employee = '{empid}'"
	# {'fieldname':'target_hours','label':'Target Hours','width':80},
	columns = [		
		{'fieldname':'employee','label':'Mitarbeiter', 'fieldtype': 'Link', 'options': 'Employee','width':140},
		{'fieldname':'log_date','label':'Datum','width':110},		
		{'fieldname':'status','label':'Status', "width": 80},
		{'fieldname':'total_work_seconds','label':_('Arbeitszeit inkl. Pause'), "width": 100, },
		# {'fieldname':'total_break_seconds','label':_('Break Hours'), "width": 110, },
		{'fieldname':'expected_break_hours','label':'Pause','width':80},
		{'fieldname':'actual_working_seconds','label':_('Arbeitszeit minus Pause'), "width": 100, },
		{'fieldname':'total_target_seconds','label':'Ziel-Arbeitszeit','width':80},
		# {'fieldname':'diff_log','label':'Diff (Work Hours - Target Seconds)','width':90},
		{'fieldname':'actual_diff_log','label':'Differenz','width':90},
		{'fieldname':'first_in','label':'Erster Checkin','width':100},
		{'fieldname':'last_out','label':'Letzter Checkout','width':100},
		{'fieldname':'name','label':'Arbeitstag',	"fieldtype": "Link", "options": "Workday", 'width':120,},		
		{'fieldname':'attendance','label':'Anwesenheitsdok.',"fieldtype": "Link", "options": "Attendance", 'width': 160},
		
	]
# 	work_data = frappe.db.sql(
#		 """		
#		 SELECT 
#				 wd.name, 
#				 wd.log_date, 
#				 wd.employee, 
#				 wd.attendance, 
#				 wd.status, 
#				 wd.total_work_seconds, 
#				 wd.total_break_seconds, 
#				 wd.actual_working_hours*60*60 as actual_working_seconds, 
#				 wd.expected_break_hours*60*60 as expected_break_hours, 
#				 wd.target_hours, 
#				 wd.total_target_seconds, 
#				 (wd.total_work_seconds - wd.total_target_seconds) as diff_log, 
#				 (wd.actual_working_hours*60*60 - wd.total_target_seconds + COALESCE(fc.sum_correction, 0)) as actual_diff_log, 
#				 TIME(wd.first_checkin) as first_in, 
#				 TIME(wd.last_checkout) as last_out 
#		 FROM 
#				 `tabWorkday` wd 
#		 LEFT JOIN (
#				 SELECT 
#						 employee, 
#						 SUM(correction) as sum_correction 
#				 FROM 
#						 `tabFlexitimeCorrection` 
#				 GROUP BY 
#						 employee
#		 ) fc ON wd.employee = fc.employee 
#		 WHERE 
#				 wd.docstatus < 2 %s %s 
#		 ORDER BY 
#				 wd.log_date ASC
#		 """%(condition_date, condition_employee), as_dict=1,
# )
	work_data = frappe.db.sql(
		f"""		
		(SELECT 
				NULL as name,
				"Stundenkonto" as log_date,
				employee, 
				"Stundenkonto Korrektur" as attendance, 
				"Korrektur" as status, 
				NULL as total_work_seconds, 
				NULL as total_break_seconds, 
				NULL as actual_working_seconds, 
				NULL as expected_break_hours, 
				NULL as target_hours, 
				NULL as total_target_seconds, 
				NULL as diff_log, 
				fc.sum_correction as actual_diff_log, 
				NULL as first_in, 
				NULL as last_out 
		FROM 
				(SELECT 
						employee, 
						SUM(IFNULL(correction,0)*60*60) as sum_correction 
				FROM 
						`tabFlexitimeCorrection` 
				GROUP BY 
						employee
				) fc)

		UNION ALL

	
		(SELECT 
				wd.name, 
				wd.log_date, 
				wd.employee, 
				wd.attendance, 
				wd.status, 
				wd.total_work_seconds, 
				wd.total_break_seconds, 
				wd.actual_working_hours*60*60 as actual_working_seconds, 
				wd.expected_break_hours*60*60 as expected_break_hours, 
				wd.target_hours, 
				wd.total_target_seconds, 
				(wd.total_work_seconds - wd.total_target_seconds) as diff_log, 
				# (wd.actual_working_hours*60*60 - wd.total_target_seconds + IFNULL(fc.sum_correction, 0)) as actual_diff_log, 
				(wd.actual_working_hours*60*60 - wd.total_target_seconds) as actual_diff_log, 
				TIME(wd.first_checkin) as first_in, 
				TIME(wd.last_checkout) as last_out 
		FROM 
				`tabWorkday` wd 
		LEFT JOIN (
				SELECT 
						employee, 
						SUM(correction) as sum_correction 
				FROM 
						`tabFlexitimeCorrection` 
				GROUP BY 
						employee
		) fc ON wd.employee = fc.employee 
		WHERE 
				wd.docstatus < 2 %s %s 
		ORDER BY 
				wd.log_date DESC)
		ORDER BY 
				log_date DESC
		"""%(condition_date, condition_employee), as_dict=1,
	)

	
	data = work_data

	return columns, data