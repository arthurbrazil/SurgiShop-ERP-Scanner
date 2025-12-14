# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

import frappe


def get_default_condition_options():
	"""
	Get the default condition options for the condition tracking feature.

	Returns:
		list[str]: Ordered list of condition option labels (no leading blank)
	"""
	return [
		'<3mo Dating',
		'Blister Damage (Cracked, Dented)',
		'Water Issue',
		'Broken Seal',
		'Expired',
		'Foreign Debris',
		'Foreign Label',
		'Kit (missing or non-verifiable components)',
		'Multiple Issues, Please Inquire',
		'Other',
		'Patient Label Issue',
		'Product Damaged',
		'Product Missing',
		'Product Mismatch',
		'Recall',
		'Residue/Markings on Primary Packaging',
		'Stains or Bio-Hazard',
		'Sterility Breach',
		'Temperature Tag Exposure',
		'Primary Label Damage',
		'Box Damaged',
	]


def build_select_options_string(option_labels):
	"""
	Build a Select options string with an empty default option.

	Args:
		option_labels (list[str]): Option labels

	Returns:
		str: Options string for a Select field
	"""
	seen = set()
	cleaned = []

	for label in option_labels or []:
		value = (label or '').strip()
		if not value:
			continue

		if value in seen:
			continue

		seen.add(value)
		cleaned.append(value)

	# Leading newline creates a blank first option
	return '\n' + '\n'.join(cleaned)


def get_condition_options_from_settings():
	"""
	Load condition options from SurgiShop Condition Settings.

	If the settings doctype does not exist yet, returns defaults.

	Returns:
		list[str]: Option labels
	"""
	try:
		doc = frappe.get_cached_doc('SurgiShop Condition Settings')
	except frappe.DoesNotExistError:
		return get_default_condition_options()

	return [(row.get('condition') or '').strip() for row in (doc.conditions or [])]


def apply_condition_options_to_custom_fields(option_labels):
	"""
	Apply the condition option list to both custom_condition Custom Fields.

	Args:
		option_labels (list[str]): Condition options
	"""
	options = build_select_options_string(option_labels)

	custom_fields = frappe.get_all(
		'Custom Field',
		filters={
			'dt': ['in', ['Purchase Receipt Item', 'Stock Ledger Entry']],
			'fieldname': 'custom_condition',
		},
		fields=['name', 'dt'],
		limit_page_length=1000,
	)

	for cf in custom_fields:
		frappe.db.set_value(
			'Custom Field',
			cf.name,
			'options',
			options,
			update_modified=False,
		)

		# Ensure updated DocField options are picked up in Desk
		frappe.clear_cache(doctype=cf.dt)


def apply_condition_options_after_migrate():
	"""
	Re-apply condition options after migrate.

	This ensures user-managed options win over fixture defaults on each migrate.
	"""
	apply_condition_options_to_custom_fields(get_condition_options_from_settings())


