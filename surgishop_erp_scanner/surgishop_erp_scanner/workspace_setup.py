# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

"""
Workspace link/shortcut injection for ERPNext v16.

Adds "SurgiShop Condition Settings" to the "SurgiShop" workspace.

In v16:
- SIDEBAR (left panel) = from `links` child table
- TILES (main area) = from `shortcuts` child table + content JSON
"""

import json

import frappe


def ensure_surgishop_workspace_condition_settings_link():
	"""
	Add "SurgiShop Condition Settings" to the "SurgiShop" workspace.
	- Adds to `links` table (for sidebar)
	- Adds to `shortcuts` table (for tiles)
	- Adds to content JSON (for rendering)
	"""
	print("\n>>> SurgiShop: Running workspace link/shortcut injection...")

	try:
		workspace_name = 'SurgiShop'
		if not frappe.db.exists('Workspace', workspace_name):
			print(f">>> SurgiShop: SKIP - Workspace '{workspace_name}' does not exist")
			return

		print(f">>> SurgiShop: FOUND - Workspace '{workspace_name}' exists")

		ws = frappe.get_doc('Workspace', workspace_name)
		target_doctype = 'SurgiShop Condition Settings'
		modified = False

		# === 1. LINKS TABLE (sidebar) ===
		existing_links = [l.get('link_to') for l in ws.links or []]
		print(f">>> SurgiShop: EXISTING LINKS: {existing_links}")

		if target_doctype not in existing_links:
			ws.append('links', {
				'label': 'SurgiShop Condition Settings',
				'link_to': target_doctype,
				'link_type': 'DocType',
				'type': 'Link',
				'hidden': 0,
				'is_query_report': 0,
				'onboard': 0,
			})
			print(">>> SurgiShop: ADDED to links table (sidebar)")
			modified = True
		else:
			print(">>> SurgiShop: Link already exists in links table")

		# === 2. SHORTCUTS TABLE (tiles) ===
		existing_shortcuts = [s.get('link_to') for s in ws.shortcuts or []]
		print(f">>> SurgiShop: EXISTING SHORTCUTS: {existing_shortcuts}")

		if target_doctype not in existing_shortcuts:
			ws.append('shortcuts', {
				'label': 'SurgiShop Condition Settings',
				'link_to': target_doctype,
				'type': 'DocType',
			})
			print(">>> SurgiShop: ADDED to shortcuts table (tiles)")
			modified = True
		else:
			print(">>> SurgiShop: Shortcut already exists in shortcuts table")

		# === 3. CONTENT JSON ===
		content = []
		try:
			content = json.loads(ws.content or '[]')
		except Exception:
			content = []

		content_has_shortcut = any(
			block.get('type') == 'shortcut' and
			(block.get('data') or {}).get('shortcut_name') == target_doctype
			for block in content
		)

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
				new_block = json.loads(json.dumps(template_block))
				new_block['id'] = 'surgishop_condition_settings_shortcut'
				new_block['data']['shortcut_name'] = target_doctype
				content.append(new_block)
				print(">>> SurgiShop: ADDED to content JSON (cloned from template)")
			else:
				content.append({
					'id': 'surgishop_condition_settings_shortcut',
					'type': 'shortcut',
					'data': {
						'shortcut_name': target_doctype,
						'col': 4
					}
				})
				print(">>> SurgiShop: ADDED to content JSON (new block)")

			ws.content = json.dumps(content)
			modified = True
		else:
			print(">>> SurgiShop: Shortcut already exists in content JSON")

		if not modified:
			print(">>> SurgiShop: SKIP - Nothing to update")
			return

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
			title='SurgiShop Workspace Link - ERROR',
			message=frappe.get_traceback(),
		)
