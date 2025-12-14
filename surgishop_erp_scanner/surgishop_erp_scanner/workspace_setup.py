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
	# Print to console so we can verify hook is running
	print("\n>>> SurgiShop: Running workspace link injection...")

	log_lines = ['=== SurgiShop Workspace Link Injection ===']

	try:
		# Step 1: Check if workspace exists
		workspace_name = 'SurgiShop'
		if not frappe.db.exists('Workspace', workspace_name):
			msg = f'SKIP: Workspace "{workspace_name}" does not exist'
			log_lines.append(msg)
			print(f">>> SurgiShop: {msg}")

			# Try to find workspaces that might contain our settings
			all_workspaces = frappe.get_all('Workspace', pluck='name')
			log_lines.append(f'Available workspaces: {all_workspaces}')
			print(f">>> SurgiShop: Available workspaces: {all_workspaces}")

			_log_info('\n'.join(log_lines))
			return

		msg = f'FOUND: Workspace "{workspace_name}" exists'
		log_lines.append(msg)
		print(f">>> SurgiShop: {msg}")

		# Step 2: Load workspace
		ws = frappe.get_doc('Workspace', workspace_name)
		msg = f'LOADED: Workspace has {len(ws.links or [])} links'
		log_lines.append(msg)
		print(f">>> SurgiShop: {msg}")

		# Step 3: List existing links for debugging
		existing_links = []
		for link in ws.links or []:
			existing_links.append({
				'label': link.get('label'),
				'link_to': link.get('link_to'),
			})
		log_lines.append(f'EXISTING LINKS: {existing_links}')
		print(f">>> SurgiShop: EXISTING LINKS: {existing_links}")

		# Step 4: Check if our link already exists
		link_exists = False
		for link in ws.links or []:
			if link.get('link_to') == 'SurgiShop Condition Settings':
				link_exists = True
				break

		if link_exists:
			msg = 'SKIP: Link already exists, nothing to do'
			log_lines.append(msg)
			print(f">>> SurgiShop: {msg}")
			_log_info('\n'.join(log_lines))
			return

		msg = 'ADDING: Link does not exist, will add it'
		log_lines.append(msg)
		print(f">>> SurgiShop: {msg}")

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
		msg = f'APPENDED: Now have {len(ws.links)} links'
		log_lines.append(msg)
		print(f">>> SurgiShop: {msg}")

		# Step 6: Fix mandatory fields
		if not ws.get('type'):
			ws.type = 'Workspace'
			msg = 'FIXED: Set ws.type = "Workspace"'
		else:
			msg = f'OK: ws.type already set to "{ws.type}"'
		log_lines.append(msg)
		print(f">>> SurgiShop: {msg}")

		# Step 7: Save
		ws.flags.ignore_mandatory = True
		ws.flags.ignore_permissions = True
		msg = 'SAVING: About to call ws.save()...'
		log_lines.append(msg)
		print(f">>> SurgiShop: {msg}")

		ws.save()
		msg = 'SAVED: ws.save() completed successfully'
		log_lines.append(msg)
		print(f">>> SurgiShop: {msg}")

		# Step 8: Commit and clear cache
		frappe.db.commit()
		msg = 'COMMITTED: frappe.db.commit() done'
		log_lines.append(msg)
		print(f">>> SurgiShop: {msg}")

		frappe.clear_cache(doctype='Workspace')
		msg = 'CACHE CLEARED: frappe.clear_cache() done'
		log_lines.append(msg)
		print(f">>> SurgiShop: {msg}")

		log_lines.append('=== SUCCESS ===')
		print(">>> SurgiShop: === SUCCESS ===\n")
		_log_info('\n'.join(log_lines))

	except Exception as e:
		msg = f'ERROR: {str(e)}'
		log_lines.append(msg)
		log_lines.append(f'TRACEBACK:\n{frappe.get_traceback()}')
		print(f">>> SurgiShop: {msg}")
		print(f">>> SurgiShop: Check Error Log for full traceback\n")
		_log_error('\n'.join(log_lines))


def _log_info(message):
	"""Log informational message to Error Log (as a note, not error)."""
	try:
		frappe.log_error(
			title='SurgiShop Workspace Link - DEBUG INFO',
			message=message,
		)
	except Exception:
		pass


def _log_error(message):
	"""Log error message to Error Log."""
	try:
		frappe.log_error(
			title='SurgiShop Workspace Link - ERROR',
			message=message,
		)
	except Exception:
		pass
