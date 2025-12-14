# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

import frappe


def sync_purchase_receipt_condition_to_sle(doc, method):
	"""
	Copy Purchase Receipt Item condition into Stock Ledger Entry.

	ERPNext links Stock Ledger Entry rows back to the source item row via
	`voucher_detail_no`, so we can map:
		PR Item.name -> SLE.voucher_detail_no

	Args:
		doc: Purchase Receipt document
		method: Hook method name (unused)
	"""
	item_condition_by_row = {}

	for item in doc.get('items') or []:
		item_condition_by_row[item.name] = item.get('custom_condition') or ''

	if not item_condition_by_row:
		return

	sle_rows = frappe.get_all(
		'Stock Ledger Entry',
		filters={
			'voucher_type': 'Purchase Receipt',
			'voucher_no': doc.name,
			'voucher_detail_no': ['in', list(item_condition_by_row.keys())],
		},
		fields=['name', 'voucher_detail_no', 'custom_condition'],
		limit_page_length=100000,
	)

	for sle in sle_rows:
		target_condition = item_condition_by_row.get(sle.voucher_detail_no, '')
		if (sle.custom_condition or '') == target_condition:
			continue

		frappe.db.set_value(
			'Stock Ledger Entry',
			sle.name,
			'custom_condition',
			target_condition,
			update_modified=False,
		)

