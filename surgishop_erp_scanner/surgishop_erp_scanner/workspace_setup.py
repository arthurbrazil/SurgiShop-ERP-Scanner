# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

"""
Simple workspace link injection for ERPNext v16.

Adds "SurgiShop Condition Settings" to the "SurgiShop" workspace sidebar.
In v16, the sidebar is rendered from the SHORTCUTS table, not the Links table.
"""

import frappe


def ensure_surgishop_workspace_condition_settings_link():
	"""
	Add "SurgiShop Condition Settings" shortcut to the "SurgiShop" workspace.
	Runs after every migrate to ensure the link is present in the sidebar.
	"""
	print("\n>>> SurgiShop: Running workspace shortcut injection...")

	try:
		workspace_name = 'SurgiShop'
		if not frappe.db.exists('Workspace', workspace_name):
			print(f">>> SurgiShop: SKIP - Workspace '{workspace_name}' does not exist")
			return

		print(f">>> SurgiShop: FOUND - Workspace '{workspace_name}' exists")

		ws = frappe.get_doc('Workspace', workspace_name)
		print(f">>> SurgiShop: LOADED - Workspace has {len(ws.shortcuts or [])} shortcuts")

		# List existing shortcuts
		existing = [s.get('link_to') for s in ws.shortcuts or []]
		print(f">>> SurgiShop: EXISTING SHORTCUTS: {existing}")

		# Check if our shortcut already exists
		if 'SurgiShop Condition Settings' in existing:
			print(">>> SurgiShop: SKIP - Shortcut already exists")
			return

		print(">>> SurgiShop: ADDING - Shortcut does not exist, will add it")

		# Add the shortcut (same structure as SurgiShop Settings)
		ws.append('shortcuts', {
			'label': 'SurgiShop Condition Settings',
			'link_to': 'SurgiShop Condition Settings',
			'type': 'DocType',
		})
		print(f">>> SurgiShop: APPENDED - Now have {len(ws.shortcuts)} shortcuts")

		# Fix mandatory fields if needed
		if not ws.get('type'):
			ws.type = 'Workspace'
			print(">>> SurgiShop: FIXED - Set ws.type = 'Workspace'")

		# Save
		ws.flags.ignore_mandatory = True
		ws.flags.ignore_permissions = True
		print(">>> SurgiShop: SAVING...")

		ws.save()
		print(">>> SurgiShop: SAVED successfully")

		frappe.db.commit()
		frappe.clear_cache(doctype='Workspace')
		print(">>> SurgiShop: COMMITTED and CACHE CLEARED")
		print(">>> SurgiShop: === SUCCESS ===\n")

	except Exception as e:
		print(f">>> SurgiShop: ERROR - {str(e)}")
		frappe.log_error(
			title='SurgiShop Workspace Shortcut - ERROR',
			message=frappe.get_traceback(),
		)
