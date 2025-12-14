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


def _workspace_has_surgishop_settings(ws):
	for link in ws.links or []:
		if (link.get('link_type') or '') != 'DocType':
			continue
		if (link.get('link_to') or '') == 'SurgiShop Settings':
			return True

	for shortcut in ws.shortcuts or []:
		if (shortcut.get('type') or '') != 'DocType':
			continue
		if (shortcut.get('link_to') or '') == 'SurgiShop Settings':
			return True

	try:
		content = json.loads(ws.content or '[]')
	except Exception:
		content = []

	for block in content:
		if block.get('type') != 'shortcut':
			continue
		data = block.get('data') or {}
		if (data.get('shortcut_name') or '') == 'SurgiShop Settings':
			return True

	return False


def _ensure_condition_settings_link_on_workspace(ws):
	label = 'SurgiShop Condition Settings'
	link_to = 'SurgiShop Condition Settings'

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


def ensure_surgishop_workspace_condition_settings_link():
	"""
	Ensure the workspace that contains SurgiShop Settings also shows
	SurgiShop Condition Settings.

	In v16, workspace rendering is cached; this runs after migrate to keep the
	link visible even if fixtures are not re-imported/overwritten.
	"""
	target_workspaces = frappe.get_all('Workspace', pluck='name', limit_page_length=1000)

	for workspace_name in target_workspaces:
		ws = frappe.get_doc('Workspace', workspace_name)
		if not _workspace_has_surgishop_settings(ws):
			continue

		_ensure_condition_settings_link_on_workspace(ws)
		ws.save(ignore_permissions=True)

	frappe.clear_cache(doctype='Workspace')

