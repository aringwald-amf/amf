# imports
import frappe
from frappe import _
from frappe.utils import add_days, today

# function to fetch the data
def execute(filters=None):
    if not filters:
        filters = {}
        
    columns, data = [], []
    columns = get_columns()
    data = get_data(filters)
    return columns, data, None, get_filters()

# define columns
def get_columns():
    columns = [
        _("Item Group") + ":Link/Item Group:150",
    ]
    
    for year in range(2019, 2024):
        for quarter in range(1, 5):
            columns.append(_(f"Y{year} Q{quarter} Produced") + ":Int:120")
            columns.append(_(f"Y{year} Q{quarter} Delivered") + ":Int:120")

    return columns



# get data
def get_data(filters):
    year_quarter_columns = []
    for year in range(2019, 2024):
        for quarter in range(1, 5):
            year_quarter_columns.append(f"SUM(CASE WHEN YEAR(posting_date) = {year} AND QUARTER(posting_date) = {quarter} THEN qty ELSE 0 END) as 'Y{year} Q{quarter}_Produced', SUM(CASE WHEN YEAR(delivery_date) = {year} AND QUARTER(delivery_date) = {quarter} THEN qty ELSE 0 END) as 'Y{year} Q{quarter}_Delivered'")

    year_quarter_columns_str = ', '.join(year_quarter_columns)

    query = f"""
        SELECT
            item_group,
            {year_quarter_columns_str}
        FROM
            (
                SELECT
                    se_item.item_group,
                    se.posting_date as posting_date,
                    NULL as delivery_date,
                    se_item.qty as qty
                FROM `tabStock Entry` se
                JOIN `tabStock Entry Detail` se_item ON se.name = se_item.parent
                WHERE se.purpose = 'Manufacture'
                AND se_item.item_group IS NOT NULL AND se_item.item_group != ''
                AND se_item.item_group NOT IN ('parts', 'raw material', 'electronic boards')

                UNION ALL

                SELECT
                    dn_item.item_group,
                    NULL as posting_date,
                    dn.posting_date as delivery_date,
                    dn_item.qty as qty
                FROM `tabDelivery Note` dn
                JOIN `tabDelivery Note Item` dn_item ON dn.name = dn_item.parent
                WHERE dn_item.item_group IS NOT NULL AND dn_item.item_group != ''
                AND dn_item.item_group NOT IN ('parts', 'raw material', 'electronic boards')
            ) combined_data
        GROUP BY item_group
        ORDER BY item_group;
    """

    # execute the query and fetch the result
    data = frappe.db.sql(query, as_list=True)
    return data





def get_filters():
    return [
        {
            "fieldname": "year",
            "label": _("Year"),
            "fieldtype": "Select",
            "options": "2019\n2020\n2021\n2022\n2023",
            "default": "",
            "width": "40",
        },
        {
            "fieldname": "quarter",
            "label": _("Quarter"),
            "fieldtype": "Select",
            "options": "1\n2\n3\n4",
            "default": "",
            "width": "40",
        },
    ]
