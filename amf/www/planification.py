import frappe

@frappe.whitelist()
def get_planning_list():
    print("get_planning_list")
    planning_list = frappe.get_all('Planning', fields=['name', 'status', 'job_card', 'qty', 'item', 'project', 'who', 'created_on', 'planned_for', 'end_date', 'delivered_qty', 'material', 'drawing', 'program', 'comments', 'filter'])
    return planning_list
