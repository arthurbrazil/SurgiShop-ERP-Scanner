# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from datetime import datetime


def get_scanner_settings():
	"""Get SurgiShop scanner settings with defaults."""
	try:
		settings = frappe.get_cached_doc("SurgiShop Settings")
		return settings
	except Exception:
		# Return defaults if settings don't exist
		return frappe._dict({
			"batch_naming_format": "{item}-{lot}",
			"auto_create_batches": 1,
			"update_missing_expiry": 1,
			"warn_on_expiry_mismatch": 1,
		})


def format_batch_id(item_code, lot, naming_format=None):
	"""Format batch ID based on naming format setting."""
	if not naming_format:
		settings = get_scanner_settings()
		naming_format = settings.get("batch_naming_format") or "{item}-{lot}"

	if naming_format == "{lot}":
		return lot
	else:
		# Default: {item}-{lot}
		return f"{item_code}-{lot}"


@frappe.whitelist()
def parse_gs1_and_get_batch(gtin, expiry, lot, item_code=None):
	"""
	API endpoint to find an item by GTIN, and then find or create a batch for it
	using the lot and expiry date.

	Args:
		gtin (str): The GTIN (Global Trade Item Number) from the barcode
		expiry (str): The expiry date in YYMMDD format
		lot (str): The lot/batch number
		item_code (str): Optional item code to validate against

	Returns:
		dict: Contains found_item, batch, gtin, expiry, lot, batch_expiry_date
		      or error information if the operation fails
	"""
	try:
		# Validate required parameters
		if not gtin or not lot:
			frappe.throw(_("GTIN and Lot Number are required."))

		# Sanitize inputs
		gtin = str(gtin).strip()
		lot = str(lot).strip()
		expiry = str(expiry).strip() if expiry else ""

		frappe.logger().info(
			f"🏥 SurgiShop ERP Scanner: Processing GS1 - GTIN: {gtin}, Lot: {lot}, Expiry: {expiry}"
		)

		# 1) Validate GTIN and get item_code from barcode
		if item_code:
			# Check if barcode exists for this specific item
			barcode_exists = frappe.db.exists("Item Barcode", {
				"barcode": gtin,
				"parent": item_code
			})
			if not barcode_exists:
				frappe.logger().info(
					f"🏥 SurgiShop ERP Scanner: GTIN {gtin} not found for item {item_code}"
				)
				frappe.throw(_("Scanned GTIN not found for the provided item code"))
			item_info = {"name": item_code}
			frappe.logger().info(
				f"🏥 SurgiShop ERP Scanner: GTIN {gtin} validated for item {item_code}"
			)
		else:
			item_info = frappe.db.get_value(
				"Item Barcode",
				{"barcode": gtin},
				["parent as name"],
				as_dict=True
			) or {}
			if not item_info:
				frappe.throw(_("No item found for GTIN: {0}. Please add this barcode to the correct Item.").format(gtin))

		# Proceed without the mismatch check, as we've validated above
		item_code = item_info.get("name")

		# 2) Verify item exists and is active
		item_info = frappe.db.get_value(
			"Item",
			item_code,
			["name", "has_batch_no", "disabled"],
			as_dict=True
		)

		if not item_info:
			error_msg = f"Item {item_code} not found in system"
			frappe.logger().error(f"🏥 SurgiShop ERP Scanner: {error_msg}")
			frappe.throw(_(error_msg))

		if item_info.get("disabled"):
			frappe.logger().warning(
				f"🏥 SurgiShop ERP Scanner: Item {item_code} is disabled"
			)
			frappe.throw(_("Item {0} is disabled").format(item_code))

		if not item_info.get("has_batch_no"):
			frappe.logger().warning(
				f"🏥 SurgiShop ERP Scanner: Item {item_code} does not use batches"
			)
			frappe.throw(_("Item {0} does not use batch numbers").format(item_code))

		# 3) Get settings and form the batch_id based on naming format
		settings = get_scanner_settings()
		batch_id = format_batch_id(item_code, lot)
		frappe.logger().info(
			f"🏥 SurgiShop ERP Scanner: Looking for batch_id: {batch_id} (format: {settings.get('batch_naming_format', '{item}-{lot}')})"
		)

		# 4) Check if the batch already exists by "batch_id"
		batch_name = frappe.db.exists("Batch", {"batch_id": batch_id})
		batch_doc = None

		if not batch_name:
			# Check if auto-create is enabled
			if not settings.get("auto_create_batches", 1):
				frappe.throw(
					_("Batch {0} does not exist and auto-create is disabled").format(batch_id)
				)

			frappe.logger().info(
				f"🏥 SurgiShop ERP Scanner: Creating new batch: {batch_id}"
			)

			# Create new batch
			new_batch = frappe.get_doc({
				"doctype": "Batch",
				"item": item_code,
				"batch_id": batch_id
			})

			# Parse and set expiry date if provided
			if expiry and len(expiry) == 6:
				try:
					# Attempt to parse YYMMDD format
					expiry_date_obj = datetime.strptime(expiry, '%y%m%d')
					new_batch.expiry_date = expiry_date_obj.strftime('%Y-%m-%d')
					frappe.logger().info(
						f"🏥 SurgiShop ERP Scanner: Parsed expiry date: {new_batch.expiry_date}"
					)
				except ValueError as ve:
					# Log warning but continue without expiry date
					frappe.logger().warning(
						f"🏥 SurgiShop ERP Scanner: Could not parse expiry date '{expiry}': {str(ve)}"
					)
					frappe.log_error(
						title="GS1 Expiry Date Parse Error",
						message=f"Could not parse expiry date: {expiry}\nError: {str(ve)}\nBatch will be created without expiry date."
					)
			elif expiry:
				frappe.logger().warning(
					f"🏥 SurgiShop ERP Scanner: Invalid expiry format (expected 6 digits): {expiry}"
				)

			# Insert batch with permission bypass
			new_batch.insert(ignore_permissions=True)
			batch_doc = new_batch
			frappe.logger().info(
				f"🏥 SurgiShop ERP Scanner: Successfully created batch: {batch_doc.name}"
			)
		else:
			# Batch already exists, retrieve it
			batch_doc = frappe.get_doc("Batch", batch_name)
			frappe.logger().info(
				f"🏥 SurgiShop ERP Scanner: Found existing batch: {batch_doc.name}"
			)

			# Check if we need to update the expiry date
			# Only update if setting is enabled, batch doesn't have expiry, and we have one from scan
			update_missing_expiry = settings.get("update_missing_expiry", 1)
			if update_missing_expiry and not batch_doc.expiry_date and expiry and len(expiry) == 6:
				try:
					# Parse the new expiry date from GS1 scan
					expiry_date_obj = datetime.strptime(expiry, '%y%m%d')
					new_expiry_date = expiry_date_obj.strftime('%Y-%m-%d')

					# Update the batch with the new expiry date
					batch_doc.expiry_date = new_expiry_date
					batch_doc.save(ignore_permissions=True)
					frappe.logger().info(
						f"🏥 SurgiShop ERP Scanner: Updated existing batch {batch_doc.name} with expiry date: {new_expiry_date}"
					)
				except ValueError as ve:
					frappe.logger().warning(
						f"🏥 SurgiShop ERP Scanner: Could not parse expiry date '{expiry}' for existing batch: {str(ve)}"
					)
			elif batch_doc.expiry_date and expiry:
				# Check for expiry mismatch warning
				warn_on_mismatch = settings.get("warn_on_expiry_mismatch", 1)
				if warn_on_mismatch and len(expiry) == 6:
					try:
						scanned_expiry = datetime.strptime(expiry, '%y%m%d').strftime('%Y-%m-%d')
						if str(batch_doc.expiry_date) != scanned_expiry:
							frappe.logger().warning(
								f"🏥 SurgiShop ERP Scanner: Expiry mismatch! Batch has {batch_doc.expiry_date}, scanned {scanned_expiry}"
							)
							# Add warning to response (will be shown to user)
							frappe.msgprint(
								_("Warning: Scanned expiry ({0}) differs from batch expiry ({1})").format(
									scanned_expiry, batch_doc.expiry_date
								),
								indicator="orange",
								alert=True
							)
					except ValueError:
						pass
				frappe.logger().info(
					f"🏥 SurgiShop ERP Scanner: Batch {batch_doc.name} already has expiry date: {batch_doc.expiry_date}"
				)

		# 5) Return found_item, final batch name, and batch_expiry_date
		result = {
			"found_item": item_code,
			"batch": batch_doc.name,
			"gtin": gtin,
			"expiry": expiry,
			"lot": lot,
			"batch_expiry_date": batch_doc.expiry_date if batch_doc.expiry_date else None
		}

		frappe.logger().info(
			f"🏥 SurgiShop ERP Scanner: GS1 parsing successful: {result}"
		)
		frappe.response["message"] = result

	except frappe.ValidationError:
		# Re-raise validation errors to show to user
		raise
	except Exception as e:
		# Log unexpected errors with full traceback
		error_msg = f"Unexpected error processing GS1 barcode: {str(e)}"
		frappe.logger().error(f"🏥 SurgiShop ERP Scanner: {error_msg}")
		frappe.log_error(
			title="GS1 Parser Unexpected Error",
			message=frappe.get_traceback()
		)
		frappe.response["message"] = {
			"found_item": None,
			"error": error_msg,
			"gtin": gtin
		}
		# Don't throw here - return error in response instead

