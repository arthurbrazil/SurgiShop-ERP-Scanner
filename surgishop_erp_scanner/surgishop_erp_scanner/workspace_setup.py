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
	log_lines = ['=== SurgiShop Workspace Link Injection ===']

	try:
		# Step 1: Check if workspace exists
		workspace_name = 'SurgiShop'
		if not frappe.db.exists('Workspace', workspace_name):
			log_lines.append(f'SKIP: Workspace "{workspace_name}" does not exist')
			# Try to find workspaces that might contain our settings
			all_workspaces = frappe.get_all('Workspace', pluck='name')
			log_lines.append(f'Available workspaces: {all_workspaces}')
			_log_info('\n'.join(log_lines))
			return

		log_lines.append(f'FOUND: Workspace "{workspace_name}" exists')

		# Step 2: Load workspace
		ws = frappe.get_doc('Workspace', workspace_name)
		log_lines.append(f'LOADED: Workspace has {len(ws.links or [])} links')

		# Step 3: List existing links for debugging
		existing_links = []
		for link in ws.links or []:
			existing_links.append({
				'label': link.get('label'),
				'link_to': link.get('link_to'),
				'link_type': link.get('link_type'),
				'type': link.get('type'),
			})
		log_lines.append(f'EXISTING LINKS: {existing_links}')

		# Step 4: Check if our link already exists
		link_exists = False
		for link in ws.links or []:
			if link.get('link_to') == 'SurgiShop Condition Settings':
				link_exists = True
				break

		if link_exists:
			log_lines.append('SKIP: Link already exists, nothing to do')
			_log_info('\n'.join(log_lines))
			return

		log_lines.append('ADDING: Link does not exist, will add it')

		# Step 5: Add the link
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
		log_lines.append(f'APPENDED: Now have {len(ws.links)} links')

		# Step 6: Fix mandatory fields
		if not ws.get('type'):
			ws.type = 'Workspace'
			log_lines.append('FIXED: Set ws.type = "Workspace"')
		else:
			log_lines.append(f'OK: ws.type already set to "{ws.type}"')

		# Step 7: Save
		ws.flags.ignore_mandatory = True
		ws.flags.ignore_permissions = True
		log_lines.append('SAVING: About to call ws.save()...')

		ws.save()
		log_lines.append('SAVED: ws.save() completed successfully')

		# Step 8: Commit and clear cache
		frappe.db.commit()
		log_lines.append('COMMITTED: frappe.db.commit() done')

		frappe.clear_cache(doctype='Workspace')
		log_lines.append('CACHE CLEARED: frappe.clear_cache() done')

		log_lines.append('=== SUCCESS ===')
		_log_info('\n'.join(log_lines))

	except Exception as e:
		log_lines.append(f'ERROR: {str(e)}')
		log_lines.append(f'TRACEBACK:\n{frappe.get_traceback()}')
		_log_error('\n'.join(log_lines))


def _log_info(message):
	"""Log informational message to Error Log (as a note, not error)."""
	frappe.log_error(
		title='SurgiShop Workspace Link - DEBUG INFO',
		message=message,
	)


def _log_error(message):
	"""Log error message to Error Log."""
	frappe.log_error(
		title='SurgiShop Workspace Link - ERROR',
		message=message,
	)
