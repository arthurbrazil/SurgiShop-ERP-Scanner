# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

"""
Simple workspace link injection for ERPNext v16.

Adds "SurgiShop Condition Settings" to the "SurgiShop" workspace sidebar,
right next to the existing "SurgiShop Settings" link.
"""

import frappe


def ensure_surgishop_workspace_condition_settings_link():
	"""
	Add "SurgiShop Condition Settings" link to the "SurgiShop" workspace.
	Runs after every migrate to ensure the link is present.
	"""
	try:
		_add_link_to_workspace('SurgiShop')
	except Exception:
		# Never break migrations due to workspace cosmetic updates
		frappe.log_error(
			title='SurgiShop ERP Scanner: workspace link injection failed',
			message=frappe.get_traceback(),
		)


def _add_link_to_workspace(workspace_name):
	"""Add the Condition Settings link to a specific workspace by name."""
	if not frappe.db.exists('Workspace', workspace_name):
		return

	ws = frappe.get_doc('Workspace', workspace_name)

	# Check if link already exists
	link_exists = False
	for link in ws.links or []:
		if link.get('link_to') == 'SurgiShop Condition Settings':
			link_exists = True
			break

	if link_exists:
		return

	# Add the link (same structure as SurgiShop Settings)
	ws.append('links', {
		'label': 'SurgiShop Condition Settings',
		'link_to': 'SurgiShop Condition Settings',
		'link_type': 'DocType',
		'type': 'Link',
		'hidden': 0,
		'is_query_report': 0,
		'link_count': 0,
		'onboard': 0,
	})

	# Fix missing mandatory field if needed (v16 requirement)
	if not ws.get('type'):
		ws.type = 'Workspace'

	# Save with bypasses to avoid validation errors on legacy workspaces
	ws.flags.ignore_mandatory = True
	ws.flags.ignore_permissions = True
	ws.save()

	frappe.db.commit()
	frappe.clear_cache(doctype='Workspace')
