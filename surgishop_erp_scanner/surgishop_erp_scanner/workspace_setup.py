# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

"""
Workspace Sidebar injection for ERPNext v16.

In v16, the left sidebar is controlled by a SEPARATE DocType called "Workspace Sidebar",
NOT the Workspace's links/shortcuts tables.

This module creates/updates the SurgiShop Workspace Sidebar to include our settings links.
"""

import frappe


def ensure_surgishop_workspace_condition_settings_link():
	"""
	Ensure "SurgiShop Condition Settings" appears in the SurgiShop workspace sidebar.
	Creates or updates the Workspace Sidebar for SurgiShop.
	"""
	print("\n>>> SurgiShop: Running Workspace Sidebar injection...")

	try:
		sidebar_name = 'SurgiShop'
		target_link = 'SurgiShop Condition Settings'

		# Check if Workspace Sidebar exists
		if frappe.db.exists('Workspace Sidebar', sidebar_name):
			print(f">>> SurgiShop: Workspace Sidebar '{sidebar_name}' exists, updating...")
			sidebar = frappe.get_doc('Workspace Sidebar', sidebar_name)

			# Check if link already exists
			existing_links = [item.get('link_to') for item in sidebar.items or []]
			print(f">>> SurgiShop: Existing sidebar items: {existing_links}")

			if target_link in existing_links:
				print(">>> SurgiShop: SKIP - Link already exists in sidebar")
				return

			# Add the new link
			sidebar.append('items', {
				'type': 'Link',
				'label': 'SurgiShop Condition Settings',
				'link_to': target_link,
				'link_type': 'DocType',
				'child': 0,
				'collapsible': 1,
				'indent': 0,
				'keep_closed': 0,
				'show_arrow': 0,
			})
			print(">>> SurgiShop: ADDED link to existing sidebar")

			sidebar.flags.ignore_permissions = True
			sidebar.save()

		else:
			print(f">>> SurgiShop: Creating new Workspace Sidebar '{sidebar_name}'...")

			sidebar = frappe.get_doc({
				'doctype': 'Workspace Sidebar',
				'name': sidebar_name,
				'title': 'SurgiShop',
				'module': 'SurgiShop ERP Scanner',
				'header_icon': 'setting',
				'items': [
					{
						'type': 'Link',
						'label': 'Home',
						'link_to': 'SurgiShop',
						'link_type': 'Workspace',
						'icon': 'home',
						'child': 0,
						'collapsible': 1,
						'indent': 0,
						'keep_closed': 0,
						'show_arrow': 0,
					},
					{
						'type': 'Link',
						'label': 'SurgiShop Settings',
						'link_to': 'SurgiShop Settings',
						'link_type': 'DocType',
						'icon': 'setting',
						'child': 0,
						'collapsible': 1,
						'indent': 0,
						'keep_closed': 0,
						'show_arrow': 0,
					},
					{
						'type': 'Link',
						'label': 'SurgiShop Condition Settings',
						'link_to': target_link,
						'link_type': 'DocType',
						'icon': 'list',
						'child': 0,
						'collapsible': 1,
						'indent': 0,
						'keep_closed': 0,
						'show_arrow': 0,
					},
				]
			})

			sidebar.flags.ignore_permissions = True
			sidebar.insert()
			print(">>> SurgiShop: CREATED new Workspace Sidebar")

		frappe.db.commit()
		frappe.clear_cache(doctype='Workspace Sidebar')
		frappe.clear_cache()
		print(">>> SurgiShop: === SUCCESS ===\n")

	except Exception as e:
		print(f">>> SurgiShop: ERROR - {str(e)}")
		frappe.log_error(
			title='SurgiShop Workspace Sidebar - ERROR',
			message=frappe.get_traceback(),
		)
