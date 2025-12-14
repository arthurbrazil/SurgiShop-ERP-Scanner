# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

import json

import frappe


def _has_link(links, label, link_to):
	for link in links or []:
		if (link.get('label') or '') == label and (link.get('link_to') or '') == link_to:
			return True
	return False


def _has_shortcut(shortcuts, label, link_to):
	for shortcut in shortcuts or []:
		if (shortcut.get('label') or '') == label and (shortcut.get('link_to') or '') == link_to:
			return True
	return False


def ensure_surgishop_workspace_condition_settings_link():
	"""
	Ensure the SS - Scanner workspace shows SurgiShop Condition Settings.

	In v16, workspace rendering is cached; this runs after migrate to keep the
	link visible even if fixtures are not re-imported/overwritten.
	"""
	workspace_name = 'SS - Scanner'
	label = 'SurgiShop Condition Settings'
	link_to = 'SurgiShop Condition Settings'

	if not frappe.db.exists('Workspace', workspace_name):
		return

	ws = frappe.get_doc('Workspace', workspace_name)

	# Links (left sidebar)
	if not _has_link(ws.links, label, link_to):
		ws.append(
			'links',
			{
				'label': label,
				'link_to': link_to,
				'link_type': 'DocType',
				'type': 'Link',
				'hidden': 0,
				'is_query_report': 0,
				'link_count': 0,
				'onboard': 0,
			},
		)

	# Shortcuts (workspace tiles)
	if not _has_shortcut(ws.shortcuts, label, link_to):
		ws.append(
			'shortcuts',
			{
				'label': label,
				'link_to': link_to,
				'type': 'DocType',
				'color': 'Blue',
				'doc_view': '',
				'stats_filter': '',
			},
		)

	# Content (optional; best-effort)
	try:
		content = json.loads(ws.content or '[]')
	except Exception:
		content = []

	needs_shortcut = True
	for block in content:
		if block.get('type') != 'shortcut':
			continue
		data = block.get('data') or {}
		if (data.get('shortcut_name') or '') == label:
			needs_shortcut = False
			break

	if needs_shortcut:
		content.append(
			{
				'id': 'surgishopConditionSettingsShortcut',
				'type': 'shortcut',
				'data': {'shortcut_name': label, 'col': 4},
			}
		)
		ws.content = json.dumps(content)

	ws.save(ignore_permissions=True)
	frappe.clear_cache(doctype='Workspace')

