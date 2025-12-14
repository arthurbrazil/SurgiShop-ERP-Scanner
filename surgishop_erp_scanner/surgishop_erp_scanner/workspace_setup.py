# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

"""
Workspace link/shortcut injection for ERPNext v16.

Adds "SurgiShop Condition Settings" to the "SurgiShop" workspace.

In v16:
- SIDEBAR (left panel) = from `links` child table + content JSON "link" blocks
- TILES (main area) = from `shortcuts` child table + content JSON "shortcut" blocks
"""

import json

import frappe


def ensure_surgishop_workspace_condition_settings_link():
	"""
	Add "SurgiShop Condition Settings" to the "SurgiShop" workspace.
	"""
	print("\n>>> SurgiShop: Running workspace link/shortcut injection...")

	try:
		workspace_name = 'SurgiShop'
		if not frappe.db.exists('Workspace', workspace_name):
			print(f">>> SurgiShop: SKIP - Workspace '{workspace_name}' does not exist")
			return

		ws = frappe.get_doc('Workspace', workspace_name)
		target_doctype = 'SurgiShop Condition Settings'
		modified = False

		# === 1. LINKS TABLE ===
		existing_links = [l.get('link_to') for l in ws.links or []]
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
			print(">>> SurgiShop: ADDED to links table")
			modified = True

		# === 2. SHORTCUTS TABLE ===
		existing_shortcuts = [s.get('link_to') for s in ws.shortcuts or []]
		if target_doctype not in existing_shortcuts:
			ws.append('shortcuts', {
				'label': 'SurgiShop Condition Settings',
				'link_to': target_doctype,
				'type': 'DocType',
			})
			print(">>> SurgiShop: ADDED to shortcuts table")
			modified = True

		# === 3. CONTENT JSON ===
		content = []
		try:
			content = json.loads(ws.content or '[]')
		except Exception:
			content = []

		# Check for shortcut block
		has_shortcut_block = any(
			block.get('type') == 'shortcut' and
			(block.get('data') or {}).get('shortcut_name') == target_doctype
			for block in content
		)

		# Check for link block
		has_link_block = any(
			block.get('type') == 'link' and
			(block.get('data') or {}).get('link_to') == target_doctype
			for block in content
		)

		if not has_shortcut_block:
			# Clone from existing SurgiShop Settings shortcut if possible
			template = None
			for block in content:
				if block.get('type') == 'shortcut':
					data = block.get('data') or {}
					if data.get('shortcut_name') == 'SurgiShop Settings':
						template = block
						break

			if template:
				new_block = json.loads(json.dumps(template))
				new_block['id'] = 'surgishop_condition_settings_shortcut'
				new_block['data']['shortcut_name'] = target_doctype
			else:
				new_block = {
					'id': 'surgishop_condition_settings_shortcut',
					'type': 'shortcut',
					'data': {'shortcut_name': target_doctype, 'col': 4}
				}
			content.append(new_block)
			print(">>> SurgiShop: ADDED shortcut block to content JSON")
			modified = True

		if not has_link_block:
			# Also add a "link" type block for sidebar
			# Clone from existing SurgiShop Settings link if possible
			template = None
			for block in content:
				if block.get('type') == 'link':
					data = block.get('data') or {}
					if data.get('link_to') == 'SurgiShop Settings':
						template = block
						break

			if template:
				new_block = json.loads(json.dumps(template))
				new_block['id'] = 'surgishop_condition_settings_link'
				new_block['data']['link_to'] = target_doctype
				if 'label' in new_block.get('data', {}):
					new_block['data']['label'] = 'SurgiShop Condition Settings'
			else:
				new_block = {
					'id': 'surgishop_condition_settings_link',
					'type': 'link',
					'data': {
						'link_to': target_doctype,
						'link_type': 'DocType',
						'label': 'SurgiShop Condition Settings'
					}
				}
			content.append(new_block)
			print(">>> SurgiShop: ADDED link block to content JSON")
			modified = True

		if modified:
			ws.content = json.dumps(content)

			if not ws.get('type'):
				ws.type = 'Workspace'

			ws.flags.ignore_mandatory = True
			ws.flags.ignore_permissions = True
			ws.save()
			print(">>> SurgiShop: SAVED")

			frappe.db.commit()
			frappe.clear_cache(doctype='Workspace')
			frappe.clear_cache()
			print(">>> SurgiShop: === SUCCESS ===\n")
		else:
			print(">>> SurgiShop: SKIP - Already exists everywhere\n")

	except Exception as e:
		print(f">>> SurgiShop: ERROR - {str(e)}")
		frappe.log_error(
			title='SurgiShop Workspace Link - ERROR',
			message=frappe.get_traceback(),
		)
