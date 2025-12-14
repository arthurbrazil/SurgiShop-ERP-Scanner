# Copyright (c) 2025, SurgiShop and Contributors
# License: MIT. See license.txt

from frappe.model.document import Document

from surgishop_erp_scanner.surgishop_erp_scanner.condition_options import (
	apply_condition_options_to_custom_fields,
	get_condition_options_from_settings,
)


class SurgiShopConditionSettings(Document):
	def on_update(self):
		apply_condition_options_to_custom_fields(get_condition_options_from_settings())

