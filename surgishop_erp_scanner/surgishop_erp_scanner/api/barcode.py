# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

import frappe
from frappe import _


@frappe.whitelist()
def scan_barcode(search_value: str, ctx: dict | str | None = None) -> dict:
	"""
	Custom barcode scanning function for SurgiShop ERP Scanner.
	Overrides ERPNext's default barcode scanning with custom logic.
	"""
	if ctx is None:
		ctx = frappe._dict()

	frappe.logger().info(
		f"🏥 SurgiShop ERP Scanner: Custom barcode scan for: {search_value}"
	)

	# Search barcode in Item Barcode table
	barcode_data = frappe.db.get_value(
		"Item Barcode",
		{"barcode": search_value},
		["barcode", "parent as item_code", "uom"],
		as_dict=True,
	)
	if barcode_data:
		frappe.logger().info(
			f"🏥 SurgiShop ERP Scanner: Found barcode in Item Barcode: {barcode_data}"
		)
		return _get_item_details(barcode_data, ctx)

	# Search serial no
	serial_no_data = frappe.db.get_value(
		"Serial No",
		search_value,
		["name as serial_no", "item_code", "batch_no"],
		as_dict=True,
	)
	if serial_no_data:
		frappe.logger().info(
			f"🏥 SurgiShop ERP Scanner: Found serial no: {serial_no_data}"
		)
		return _get_item_details(serial_no_data, ctx)

	# Search batch no
	batch_no_data = frappe.db.get_value(
		"Batch",
		search_value,
		["name as batch_no", "item as item_code"],
		as_dict=True,
	)
	if batch_no_data:
		if frappe.get_cached_value("Item", batch_no_data.item_code, "has_serial_no"):
			frappe.throw(
				_(
					"Batch No {0} is linked with Item {1} which has serial no. Please scan serial no instead."
				).format(search_value, batch_no_data.item_code)
			)

		frappe.logger().info(
			f"🏥 SurgiShop ERP Scanner: Found batch no: {batch_no_data}"
		)
		return _get_item_details(batch_no_data, ctx)

	# Search warehouse
	warehouse = frappe.get_cached_value(
		"Warehouse",
		search_value,
		("name", "disabled"),
		as_dict=True
	)
	if warehouse and not warehouse.disabled:
		warehouse_data = {"warehouse": warehouse.name}
		frappe.logger().info(
			f"🏥 SurgiShop ERP Scanner: Found warehouse: {warehouse_data}"
		)
		return warehouse_data

	# If no match found, return empty dict
	frappe.logger().info(
		f"🏥 SurgiShop ERP Scanner: No match found for: {search_value}"
	)
	return {}


def _get_item_details(scan_result: dict, ctx: dict) -> dict:
	"""Get additional item details for the scan result."""
	item_code = scan_result.get("item_code")
	if not item_code:
		return scan_result

	# Get item details
	item_info = frappe.get_cached_value(
		"Item",
		item_code,
		("has_batch_no", "has_serial_no", "item_name", "stock_uom", "is_stock_item"),
		as_dict=True,
	)

	if item_info:
		scan_result.update(item_info)

	# Get default warehouse if available
	if ctx and hasattr(ctx, 'get'):
		try:
			from erpnext.stock.get_item_details import get_item_warehouse_
			if warehouse := get_item_warehouse_(
				ctx,
				frappe._dict(name=item_code),
				overwrite_warehouse=True
			):
				scan_result["default_warehouse"] = warehouse
		except Exception:
			pass

	# Get item rate if available
	try:
		from erpnext.stock.get_item_details import get_item_details
		item_details = get_item_details({
			"item_code": item_code,
			"company": ctx.get("company") if ctx else None,
			"warehouse": ctx.get("set_warehouse") if ctx else None,
		})

		if item_details:
			scan_result["rate"] = item_details.get("rate", 0)
			scan_result["stock_uom"] = item_details.get(
				"stock_uom",
				item_info.get("stock_uom") if item_info else None
			)
	except Exception as e:
		frappe.logger().error(
			f"🏥 SurgiShop ERP Scanner: Error getting item details: {str(e)}"
		)

	frappe.logger().info(
		f"🏥 SurgiShop ERP Scanner: Enhanced scan result: {scan_result}"
	)
	return scan_result


@frappe.whitelist()
def get_item_by_barcode(barcode: str) -> dict:
	"""
	Get item details by barcode.
	Simple API for barcode lookup.
	"""
	result = scan_barcode(barcode)
	return result


@frappe.whitelist()
def validate_barcode(barcode: str) -> bool:
	"""
	Validate if a barcode exists in the system.
	"""
	if not barcode:
		return False

	# Check if barcode exists in any of the tables
	exists = (
		frappe.db.exists("Item Barcode", {"barcode": barcode}) or
		frappe.db.exists("Serial No", barcode) or
		frappe.db.exists("Batch", barcode) or
		frappe.db.exists("Warehouse", barcode)
	)

	return bool(exists)


@frappe.whitelist()
def get_condition_options() -> list:
	"""
	Get condition options from SurgiShop Condition Settings.
	This endpoint bypasses direct DocType permission checks.
	"""
	try:
		doc = frappe.get_cached_doc("SurgiShop Condition Settings")
		options = []
		for row in (doc.conditions or []):
			condition = (row.get("condition") or "").strip()
			if condition:
				options.append(condition)
		return options
	except frappe.DoesNotExistError:
		return []
	except Exception:
		return []

