# Copyright (c) 2024, SurgiShop and Contributors
# License: MIT. See license.txt

import frappe
from frappe.model.document import Document


class SurgiShopSettings(Document):
	"""
	Settings for SurgiShop ERPNext customizations.
	
	This Single DocType provides configuration options for:
	- Batch expiry validation overrides
	- Inbound transaction settings
	"""
	
	@staticmethod
	def get_settings():
		"""
		Get the current SurgiShop settings.
		Returns a cached version for performance.
		"""
		return frappe.get_cached_doc("SurgiShop Settings")
	
	def validate(self):
		"""Validate settings before saving."""
		# If skip_batch_expiry_validation is enabled, show a warning
		if self.skip_batch_expiry_validation:
			frappe.msgprint(
				frappe._("Warning: All batch expiry validation has been disabled. "
					"Expired products can now be sold/delivered."),
				indicator="orange",
				alert=True
			)
