# Copyright (c) 2024, SurgiShop and Contributors
# License: MIT. See license.txt

import frappe


def after_install():
	"""
	Run after the app is installed.
	Creates default SurgiShop Settings if they don't exist.
	"""
	create_default_settings()


def create_default_settings():
	"""Create default SurgiShop Settings document."""
	if not frappe.db.exists("SurgiShop Settings", "SurgiShop Settings"):
		doc = frappe.new_doc("SurgiShop Settings")
		doc.allow_expired_batches_on_inbound = 1
		doc.skip_batch_expiry_validation = 0
		doc.allow_expired_on_purchase_receipt = 1
		doc.allow_expired_on_purchase_invoice = 1
		doc.allow_expired_on_stock_entry_receipt = 1
		doc.allow_expired_on_stock_reconciliation = 1
		doc.allow_expired_on_sales_return = 1
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		print("SurgiShop Settings created successfully.")

