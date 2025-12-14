app_name = "surgishop_erp_scanner"
app_title = "SurgiShop ERP Scanner"
app_publisher = "SurgiShop"
app_description = "SurgiShop ERP Scanner - Batch expiry validation overrides for ERPNext"
app_email = "Arthur.Borges@SurgiShop.com"
app_license = "mit"

# Required Frappe version
required_frappe_version = ">=16.0.0"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "surgishop_erp_scanner",
# 		"logo": "/assets/surgishop_erp_scanner/logo.png",
# 		"title": "SurgiShop ERP Scanner",
# 		"route": "/surgishop_erp_scanner",
# 		"has_permission": "surgishop_erp_scanner.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/surgishop_erp_scanner/css/surgishop_erp_scanner.css"
app_include_js = [
	"/assets/surgishop_erp_scanner/js/gs1-utils.js",
	"/assets/surgishop_erp_scanner/js/custom-barcode-scanner.js",
	"/assets/surgishop_erp_scanner/js/custom-serial-batch-selector.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/surgishop_erp_scanner/css/surgishop_erp_scanner.css"
# web_include_js = "/assets/surgishop_erp_scanner/js/surgishop_erp_scanner.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "surgishop_erp_scanner/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "surgishop_erp_scanner/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "surgishop_erp_scanner.utils.jinja_methods",
# 	"filters": "surgishop_erp_scanner.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "surgishop_erp_scanner.install.before_install"
after_install = "surgishop_erp_scanner.surgishop_erp_scanner.install.after_install"

# Ensure condition options are always applied after migrations, so user-managed
# options win over fixture defaults.
after_migrate = [
	"surgishop_erp_scanner.surgishop_erp_scanner.condition_options.apply_condition_options_after_migrate",
	"surgishop_erp_scanner.surgishop_erp_scanner.workspace_setup.ensure_surgishop_workspace_condition_settings_link"
]

# Uninstallation
# ------------

# before_uninstall = "surgishop_erp_scanner.uninstall.before_uninstall"
# after_uninstall = "surgishop_erp_scanner.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "surgishop_erp_scanner.utils.before_app_install"
# after_app_install = "surgishop_erp_scanner.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "surgishop_erp_scanner.utils.before_app_uninstall"
# after_app_uninstall = "surgishop_erp_scanner.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "surgishop_erp_scanner.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Purchase Receipt": {
		"validate": "surgishop_erp_scanner.surgishop_erp_scanner.overrides.stock_controller.validate_serialized_batch_with_expired_override",
		"on_submit": "surgishop_erp_scanner.surgishop_erp_scanner.overrides.condition_tracking.sync_purchase_receipt_condition_to_sle"
	},
	"Purchase Invoice": {
		"validate": "surgishop_erp_scanner.surgishop_erp_scanner.overrides.stock_controller.validate_serialized_batch_with_expired_override"
	},
	"Stock Entry": {
		"validate": "surgishop_erp_scanner.surgishop_erp_scanner.overrides.stock_controller.validate_serialized_batch_with_expired_override"
	},
	"Stock Reconciliation": {
		"validate": "surgishop_erp_scanner.surgishop_erp_scanner.overrides.stock_controller.validate_serialized_batch_with_expired_override"
	},
	"Sales Invoice": {
		"validate": "surgishop_erp_scanner.surgishop_erp_scanner.overrides.stock_controller.validate_serialized_batch_with_expired_override"
	},
	"Delivery Note": {
		"validate": "surgishop_erp_scanner.surgishop_erp_scanner.overrides.stock_controller.validate_serialized_batch_with_expired_override"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"surgishop_erp_scanner.tasks.all"
# 	],
# 	"daily": [
# 		"surgishop_erp_scanner.tasks.daily"
# 	],
# 	"hourly": [
# 		"surgishop_erp_scanner.tasks.hourly"
# 	],
# 	"weekly": [
# 		"surgishop_erp_scanner.tasks.weekly"
# 	],
# 	"monthly": [
# 		"surgishop_erp_scanner.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "surgishop_erp_scanner.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "surgishop_erp_scanner.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "surgishop_erp_scanner.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["surgishop_erp_scanner.utils.before_request"]
# after_request = ["surgishop_erp_scanner.utils.after_request"]

# Job Events
# ----------
# before_job = ["surgishop_erp_scanner.utils.before_job"]
# after_job = ["surgishop_erp_scanner.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"surgishop_erp_scanner.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Fixtures
# --------
# Export these doctypes when running bench export-fixtures

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			["dt", "in", ["Purchase Receipt Item", "Stock Ledger Entry"]],
			["fieldname", "=", "custom_condition"]
		]
	}
]
