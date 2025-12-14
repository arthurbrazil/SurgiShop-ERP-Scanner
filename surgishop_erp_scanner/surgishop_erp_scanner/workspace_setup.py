# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

import json

import frappe


def _clone_child_doc(child_dt, template_name, overrides):
	meta = frappe.get_meta(child_dt)
	template = frappe.get_doc(child_dt, template_name)
	new_doc = frappe.new_doc(child_dt)

	for field in meta.fields:
		fieldname = field.fieldname
		if not fieldname:
			continue
		if fieldname in ['name', 'owner', 'creation', 'modified', 'modified_by', 'docstatus']:
			continue

		if fieldname in overrides:
			new_doc.set(fieldname, overrides[fieldname])
			continue

		new_doc.set(fieldname, template.get(fieldname))

	for key, value in (overrides or {}).items():
		new_doc.set(key, value)

	return new_doc


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
	try:
		meta = frappe.get_meta('Workspace')
		links_child_dt = meta.get_field('links').options
		shortcuts_child_dt = meta.get_field('shortcuts').options

		# Prefer DB-driven detection: find the Workspace that already has a sidebar
		# link to "SurgiShop Settings", since that's exactly where we want to add the
		# Condition Settings link.
		target_workspaces = list(
			set(
				frappe.get_all(
					links_child_dt,
					filters={
						'parenttype': 'Workspace',
						'parentfield': 'links',
						'link_to': 'SurgiShop Settings',
					},
					pluck='parent',
					limit_page_length=1000,
				)
			)
		)

		# Fallback: scan all workspaces if the DB query finds none (e.g. if the
		# workspace only uses content JSON/shortcuts).
		if not target_workspaces:
			target_workspaces = frappe.get_all('Workspace', pluck='name', limit_page_length=1000)

		for workspace_name in target_workspaces:
			ws = frappe.get_doc('Workspace', workspace_name)
			if not _workspace_has_surgishop_settings(ws):
				continue

			# Keep the row healthy for v16 (some legacy workspaces may be missing it)
			if not ws.get('type'):
				frappe.db.set_value(
					'Workspace',
					workspace_name,
					'type',
					'Module',
					update_modified=False,
				)

			# Insert Link row without saving parent Workspace (avoids mandatory errors)
			label = 'SurgiShop Condition Settings'
			link_to = 'SurgiShop Condition Settings'

			if not frappe.db.exists(
				links_child_dt,
				{
					'parent': workspace_name,
					'parenttype': 'Workspace',
					'parentfield': 'links',
					'link_to': link_to,
				},
			):
				template_rows = frappe.get_all(
					links_child_dt,
					filters={
						'parent': workspace_name,
						'parenttype': 'Workspace',
						'parentfield': 'links',
						'link_to': 'SurgiShop Settings',
					},
					pluck='name',
					limit_page_length=1,
				)

				if template_rows:
					_clone_child_doc(
						links_child_dt,
						template_rows[0],
						{
							'parent': workspace_name,
							'parenttype': 'Workspace',
							'parentfield': 'links',
							'label': label,
							'link_to': link_to,
						},
					).insert(ignore_permissions=True)
				else:
					frappe.get_doc(
						{
							'doctype': links_child_dt,
							'parent': workspace_name,
							'parenttype': 'Workspace',
							'parentfield': 'links',
							'label': label,
							'link_to': link_to,
							'link_type': 'DocType',
							'type': 'Link',
							'hidden': 0,
							'is_query_report': 0,
							'link_count': 0,
							'onboard': 0,
						}
					).insert(ignore_permissions=True)

			# Insert Shortcut row without saving parent Workspace
			if not frappe.db.exists(
				shortcuts_child_dt,
				{
					'parent': workspace_name,
					'parenttype': 'Workspace',
					'parentfield': 'shortcuts',
					'link_to': link_to,
				},
			):
				template_rows = frappe.get_all(
					shortcuts_child_dt,
					filters={
						'parent': workspace_name,
						'parenttype': 'Workspace',
						'parentfield': 'shortcuts',
						'link_to': 'SurgiShop Settings',
					},
					pluck='name',
					limit_page_length=1,
				)

				if template_rows:
					_clone_child_doc(
						shortcuts_child_dt,
						template_rows[0],
						{
							'parent': workspace_name,
							'parenttype': 'Workspace',
							'parentfield': 'shortcuts',
							'label': label,
							'link_to': link_to,
						},
					).insert(ignore_permissions=True)
				else:
					frappe.get_doc(
						{
							'doctype': shortcuts_child_dt,
							'parent': workspace_name,
							'parenttype': 'Workspace',
							'parentfield': 'shortcuts',
							'label': label,
							'link_to': link_to,
							'type': 'DocType',
							'color': 'Blue',
							'doc_view': '',
							'stats_filter': '',
						}
					).insert(ignore_permissions=True)

			# Best-effort: add tile to content JSON (DB-level update, no parent save)
			try:
				content = json.loads(ws.content or '[]')
			except Exception:
				content = []

			template_block = None
			has_condition_block = False

			for block in content:
				if block.get('type') != 'shortcut':
					continue
				data = block.get('data') or {}

				if (data.get('shortcut_name') or '') == label:
					has_condition_block = True

				if (data.get('shortcut_name') or '') == 'SurgiShop Settings':
					template_block = block

			if not has_condition_block:
				if template_block:
					new_block = json.loads(json.dumps(template_block))
					new_block['id'] = 'surgishopConditionSettingsShortcut'
					new_block.setdefault('data', {})
					new_block['data']['shortcut_name'] = label
					content.append(new_block)
				else:
					content.append(
						{
							'id': 'surgishopConditionSettingsShortcut',
							'type': 'shortcut',
							'data': {'shortcut_name': label, 'col': 4},
						}
					)

				frappe.db.set_value(
					'Workspace',
					workspace_name,
					'content',
					json.dumps(content),
					update_modified=False,
				)

		# Clear caches so Desk sidebar/workspace page refresh picks up changes.
		frappe.clear_cache(doctype='Workspace')
		frappe.clear_cache()
	except Exception:
		# Never break migrations due to workspace cosmetic updates
		frappe.log_error(
			title='SurgiShop ERP Scanner: workspace after_migrate failed',
			message=frappe.get_traceback(),
		)

