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
	cleanup_old_workspaces()


def cleanup_old_workspaces():
	"""
	Remove old/renamed workspaces to prevent duplicates.
	Called after install and can be called after migrate.
	"""
	old_workspaces = ["SS - Scanner"]

	for ws_name in old_workspaces:
		if frappe.db.exists("Workspace", ws_name):
			try:
				frappe.delete_doc("Workspace", ws_name, force=True, ignore_permissions=True)
				frappe.db.commit()
				print(f"Deleted old workspace: {ws_name}")
			except Exception as e:
				print(f"Could not delete workspace {ws_name}: {e}")


def fix_settings_defaults():
	"""
	Fix default values for settings fields that were added after initial install.
	This ensures new Check fields have the correct default (1) instead of 0.
	"""
	try:
		if frappe.db.exists("SurgiShop Settings", "SurgiShop Settings"):
			# Fields that should default to 1 (enabled) if they are 0 or None
			fields_to_enable = [
				"prompt_create_item_on_unknown_gtin",
			]

			doc = frappe.get_doc("SurgiShop Settings")
			updated = False

			for field in fields_to_enable:
				current_value = doc.get(field)
				# If value is 0 or None, set it to 1
				if current_value in (0, None, ""):
					doc.set(field, 1)
					updated = True
					print(f"Fixed {field}: {current_value} -> 1")

			if updated:
				doc.save(ignore_permissions=True)
				frappe.db.commit()
				print("SurgiShop Settings defaults fixed.")
	except Exception as e:
		print(f"Could not fix settings defaults: {e}")


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

