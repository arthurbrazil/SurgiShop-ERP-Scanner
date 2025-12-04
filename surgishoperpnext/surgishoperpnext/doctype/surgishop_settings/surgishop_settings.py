# Copyright (c) 2024, SurgiShop and Contributors
# License: MIT. See license.txt

import frappe
from frappe.model.document import Document


class SurgiShopSettings(Document):
	"""
	Settings for SurgiShop ERPNext customizations.
	
	This Single DocType provides configuration options for:
	- Batch expiry validation overrides
	- Inbound transaction settings
	"""
	
	@staticmethod
	def get_settings():
		"""
		Get the current SurgiShop settings.
		Returns a cached version for performance.
		"""
		return frappe.get_cached_doc("SurgiShop Settings")
	
	def validate(self):
		"""Validate settings before saving."""
		# If skip_batch_expiry_validation is enabled, show a warning
		if self.skip_batch_expiry_validation:
			frappe.msgprint(
				frappe._("Warning: All batch expiry validation has been disabled. "
					"Expired products can now be sold/delivered."),
				indicator="orange",
				alert=True
			)


def get_surgishop_settings():
	"""
	Utility function to get SurgiShop settings.
	Creates default settings if they don't exist.
	"""
	try:
		return frappe.get_cached_doc("SurgiShop Settings")
	except frappe.DoesNotExistError:
		# Create default settings if not exists
		doc = frappe.new_doc("SurgiShop Settings")
		doc.insert(ignore_permissions=True)
		return doc


def is_expired_batch_allowed(doctype, purpose=None, is_return=False):
	"""
	Check if expired batches are allowed for the given document type.
	
	Args:
		doctype: The document type (e.g., "Purchase Receipt", "Stock Entry")
		purpose: For Stock Entry, the purpose (e.g., "Material Receipt")
		is_return: Whether the document is a return
	
	Returns:
		bool: True if expired batches should be allowed
	"""
	settings = get_surgishop_settings()
	
	# If all validation is skipped, allow everything
	if settings.skip_batch_expiry_validation:
		return True
	
	# If inbound override is disabled, don't allow
	if not settings.allow_expired_batches_on_inbound:
		return False
	
	# Check specific document type settings
	if doctype == "Purchase Receipt" and not is_return:
		return settings.allow_expired_on_purchase_receipt
	
	if doctype == "Purchase Invoice" and not is_return:
		return settings.allow_expired_on_purchase_invoice
	
	if doctype == "Stock Entry" and purpose == "Material Receipt":
		return settings.allow_expired_on_stock_entry_receipt
	
	if doctype == "Stock Reconciliation":
		return settings.allow_expired_on_stock_reconciliation
	
	if doctype in ["Sales Invoice", "Delivery Note"] and is_return:
		return settings.allow_expired_on_sales_return
	
	return False

