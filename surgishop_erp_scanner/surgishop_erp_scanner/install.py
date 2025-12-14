# Copyright (c) 2024, SurgiShop and Contributors
# License: MIT. See license.txt

import frappe

from surgishop_erp_scanner.surgishop_erp_scanner.condition_options import (
	apply_condition_options_to_custom_fields,
	get_default_condition_options,
)


def after_install():
	"""
	Run after the app is installed.
	Creates default SurgiShop Settings if they don't exist.
	"""
	create_default_settings()
	create_default_condition_settings()


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


def create_default_condition_settings():
	"""
	Create default SurgiShop Condition Settings document.

	Also ensures the custom field Select options are updated to match.
	"""
	if not frappe.db.exists('SurgiShop Condition Settings', 'SurgiShop Condition Settings'):
		doc = frappe.new_doc('SurgiShop Condition Settings')
		doc.conditions = []

		for label in get_default_condition_options():
			doc.append('conditions', {'condition': label})

		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		print('SurgiShop Condition Settings created successfully.')

	apply_condition_options_to_custom_fields(get_default_condition_options())

