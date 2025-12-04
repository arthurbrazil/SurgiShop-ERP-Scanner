# Copyright (c) 2024, SurgiShop and Contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.utils import getdate, get_link_to_form, flt

# Handle potential import path changes between ERPNext versions
try:
	from erpnext.controllers.stock_controller import BatchExpiredError
except ImportError:
	# Fallback for different ERPNext versions
	try:
		from erpnext.stock.doctype.batch.batch import BatchExpiredError
	except ImportError:
		# Create custom exception if not found
		class BatchExpiredError(frappe.ValidationError):
			pass


def get_surgishop_settings():
	"""
	Get SurgiShop settings with fallback defaults.
	Returns a dict-like object with settings values.
	"""
	try:
		return frappe.get_cached_doc("SurgiShop Settings")
	except frappe.DoesNotExistError:
		# Return default values if settings don't exist yet
		return frappe._dict({
			"allow_expired_batches_on_inbound": True,
			"skip_batch_expiry_validation": False,
			"allow_expired_on_purchase_receipt": True,
			"allow_expired_on_purchase_invoice": True,
			"allow_expired_on_stock_entry_receipt": True,
			"allow_expired_on_stock_reconciliation": True,
			"allow_expired_on_sales_return": True,
		})


def is_expired_batch_allowed_for_doc(doc, item_row):
	"""
	Check if expired batches are allowed based on settings and document type.
	
	Args:
		doc: The document being validated
		item_row: The item row being checked
	
	Returns:
		bool: True if expired batches should be allowed
	"""
	settings = get_surgishop_settings()
	
	# If all validation is skipped, allow everything
	if settings.skip_batch_expiry_validation:
		return True
	
	# If inbound override is disabled globally, don't allow
	if not settings.allow_expired_batches_on_inbound:
		return False
	
	is_return = doc.get("is_return", False)
	
	# Purchase Receipt (non-return)
	if doc.doctype == "Purchase Receipt" and not is_return:
		return settings.allow_expired_on_purchase_receipt
	
	# Purchase Invoice (non-return)
	if doc.doctype == "Purchase Invoice" and not is_return:
		return settings.allow_expired_on_purchase_invoice
	
	# Stock Entry with Material Receipt purpose
	if doc.doctype == "Stock Entry" and doc.purpose == "Material Receipt":
		return settings.allow_expired_on_stock_entry_receipt
	
	# Stock Entry with Material Transfer - check if it's moving TO a warehouse only
	if doc.doctype == "Stock Entry" and doc.purpose == "Material Transfer":
		if item_row.get("t_warehouse") and not item_row.get("s_warehouse"):
			return settings.allow_expired_on_stock_entry_receipt
	
	# Stock Reconciliation (positive quantities = inbound)
	if doc.doctype == "Stock Reconciliation" and flt(item_row.get("qty", 0)) > 0:
		return settings.allow_expired_on_stock_reconciliation
	
	# Sales returns (Sales Invoice / Delivery Note with is_return)
	if doc.doctype in ["Sales Invoice", "Delivery Note"] and is_return:
		return settings.allow_expired_on_sales_return
	
	# Purchase returns are outbound - don't allow expired
	if doc.doctype in ["Purchase Invoice", "Purchase Receipt"] and is_return:
		return False
	
	return False


def get_serial_nos_helper(serial_no_str):
	"""
	Get serial numbers from a string, handling different ERPNext versions.
	"""
	try:
		from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
		return get_serial_nos(serial_no_str)
	except ImportError:
		# Fallback: simple split by newline
		if not serial_no_str:
			return []
		return [s.strip() for s in serial_no_str.strip().split('\n') if s.strip()]


def validate_serialized_batch_with_expired_override(doc, method):
	"""
	Override the validate_serialized_batch method to allow expired products 
	for inbound transactions based on SurgiShop Settings.
	
	This is called via doc_events hook for better update-proofing.
	Compatible with Frappe/ERPNext v15 and v16.
	"""
	settings = get_surgishop_settings()
	
	# If all validation is skipped, only validate serial/batch relationship
	skip_expiry_check = settings.skip_batch_expiry_validation

	is_material_issue = False
	if doc.doctype == "Stock Entry" and doc.purpose in ["Material Issue", "Material Transfer"]:
		is_material_issue = True

	for d in doc.get("items"):
		# Validate serial number belongs to batch (always enforced)
		if hasattr(d, "serial_no") and hasattr(d, "batch_no") and d.serial_no and d.batch_no:
			serial_nos = frappe.get_all(
				"Serial No",
				fields=["batch_no", "name", "warehouse"],
				filters={"name": ("in", get_serial_nos_helper(d.serial_no))},
			)

			for row in serial_nos:
				if row.warehouse and row.batch_no != d.batch_no:
					frappe.throw(
						_("Row #{0}: Serial No {1} does not belong to Batch {2}").format(
							d.idx, row.name, d.batch_no
						)
					)

		# Skip all expiry validation if setting is enabled
		if skip_expiry_check:
			continue

		# Skip batch expiry validation for material issues
		if is_material_issue:
			continue

		# Skip batch expiry validation if allowed for this document type
		if is_expired_batch_allowed_for_doc(doc, d):
			continue

		# Keep the original batch expiry validation for outbound transactions
		if (
			flt(d.qty) > 0.0 
			and d.get("batch_no") 
			and doc.get("posting_date") 
			and doc.docstatus < 2
		):
			expiry_date = frappe.get_cached_value("Batch", d.get("batch_no"), "expiry_date")

			if expiry_date and getdate(expiry_date) < getdate(doc.posting_date):
				frappe.throw(
					_("Row #{0}: The batch {1} has already expired.").format(
						d.idx, get_link_to_form("Batch", d.get("batch_no"))
					),
					BatchExpiredError,
				)
