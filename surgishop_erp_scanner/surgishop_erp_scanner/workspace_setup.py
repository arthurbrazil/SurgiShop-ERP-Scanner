# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

"""
Workspace shortcut injection for ERPNext v16.

Adds "SurgiShop Condition Settings" to the "SurgiShop" workspace sidebar.
In v16, the sidebar is rendered from BOTH the shortcuts table AND the content JSON.
"""

import json

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

		# Check shortcuts table
		existing_shortcuts = [s.get('link_to') for s in ws.shortcuts or []]
		print(f">>> SurgiShop: EXISTING SHORTCUTS: {existing_shortcuts}")

		shortcut_exists = 'SurgiShop Condition Settings' in existing_shortcuts

		# Check content JSON
		content = []
		try:
			content = json.loads(ws.content or '[]')
		except Exception:
			content = []

		content_has_shortcut = False
		for block in content:
			if block.get('type') == 'shortcut':
				data = block.get('data') or {}
				if data.get('shortcut_name') == 'SurgiShop Condition Settings':
					content_has_shortcut = True
					break

		print(f">>> SurgiShop: shortcut_exists={shortcut_exists}, content_has_shortcut={content_has_shortcut}")

		if shortcut_exists and content_has_shortcut:
			print(">>> SurgiShop: SKIP - Already exists in both places")
			return

		# Add to shortcuts table if missing
		if not shortcut_exists:
			ws.append('shortcuts', {
				'label': 'SurgiShop Condition Settings',
				'link_to': 'SurgiShop Condition Settings',
				'type': 'DocType',
			})
			print(">>> SurgiShop: ADDED to shortcuts table")

		# Add to content JSON if missing
		if not content_has_shortcut:
			# Find existing SurgiShop Settings shortcut block to clone structure
			template_block = None
			for block in content:
				if block.get('type') == 'shortcut':
					data = block.get('data') or {}
					if data.get('shortcut_name') == 'SurgiShop Settings':
						template_block = block
						break

			if template_block:
				# Clone the template
				new_block = json.loads(json.dumps(template_block))
				new_block['id'] = 'surgishop_condition_settings_shortcut'
				new_block['data']['shortcut_name'] = 'SurgiShop Condition Settings'
				content.append(new_block)
				print(">>> SurgiShop: ADDED to content JSON (cloned from template)")
			else:
				# Create new block
				content.append({
					'id': 'surgishop_condition_settings_shortcut',
					'type': 'shortcut',
					'data': {
						'shortcut_name': 'SurgiShop Condition Settings',
						'col': 4
					}
				})
				print(">>> SurgiShop: ADDED to content JSON (new block)")

			ws.content = json.dumps(content)

		# Fix mandatory fields
		if not ws.get('type'):
			ws.type = 'Workspace'

		# Save
		ws.flags.ignore_mandatory = True
		ws.flags.ignore_permissions = True
		print(">>> SurgiShop: SAVING...")

		ws.save()
		print(">>> SurgiShop: SAVED")

		frappe.db.commit()
		frappe.clear_cache(doctype='Workspace')
		frappe.clear_cache()
		print(">>> SurgiShop: COMMITTED and ALL CACHES CLEARED")
		print(">>> SurgiShop: === SUCCESS ===\n")

	except Exception as e:
		print(f">>> SurgiShop: ERROR - {str(e)}")
		frappe.log_error(
			title='SurgiShop Workspace Shortcut - ERROR',
			message=frappe.get_traceback(),
		)
