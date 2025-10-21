app_name = "surgishoperpnext"
app_title = "SurgiShopERPNext"
app_publisher = "SurgiShop"
app_description = "ERPNext app for allowing expired products in transactions for research purposes"
app_email = "Arthur.Borges@SurgiShop.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "surgishoperpnext",
# 		"logo": "/assets/surgishoperpnext/logo.png",
# 		"title": "SurgiShopERPNext",
# 		"route": "/surgishoperpnext",
# 		"has_permission": "surgishoperpnext.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/surgishoperpnext/css/surgishoperpnext.css"
# Load gs1-utils.js FIRST (custom-barcode-scanner.js depends on it)
app_include_js = [
	"/assets/surgishoperpnext/js/gs1-utils.js?v=0.3.5",
	"/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=0.3.5",
	"/assets/surgishoperpnext/js/custom-serial-batch-selector.js?v=0.3.5"
]

# include js, css files in header of web template
# web_include_css = "/assets/surgishoperpnext/css/surgishoperpnext.css"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# Load custom barcode scanner for specific doctypes
# doctype_js = {
# 	"Stock Entry": "/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=1.0.7",
# 	"Purchase Order": "/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=1.0.7",
# 	"Purchase Receipt": "/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=1.0.7",
# 	"Purchase Invoice": "/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=1.0.7",
# 	"Sales Invoice": "/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=1.0.7",
# 	"Delivery Note": "/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=1.0.7",
# 	"Stock Reconciliation": "/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=1.0.7"
# }

# Add to doctype_js
doctype_js = {
	"Stock Entry": [
		"/assets/surgishoperpnext/js/gs1-parser.min.js",
		"/assets/surgishoperpnext/js/gs1-utils.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-serial-batch-selector.js?v=0.3.5"
	],
	"Purchase Receipt": [
		"/assets/surgishoperpnext/js/gs1-parser.min.js",
		"/assets/surgishoperpnext/js/gs1-utils.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-serial-batch-selector.js?v=0.3.5"
	],
	"Purchase Invoice": [
		"/assets/surgishoperpnext/js/gs1-parser.min.js",
		"/assets/surgishoperpnext/js/gs1-utils.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-serial-batch-selector.js?v=0.3.5"
	],
	"Sales Invoice": [
		"/assets/surgishoperpnext/js/gs1-parser.min.js",
		"/assets/surgishoperpnext/js/gs1-utils.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-serial-batch-selector.js?v=0.3.5"
	],
	"Delivery Note": [
		"/assets/surgishoperpnext/js/gs1-parser.min.js",
		"/assets/surgishoperpnext/js/gs1-utils.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-serial-batch-selector.js?v=0.3.5"
	],
	"Stock Reconciliation": [
		"/assets/surgishoperpnext/js/gs1-parser.min.js",
		"/assets/surgishoperpnext/js/gs1-utils.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=0.3.5",
		"/assets/surgishoperpnext/js/custom-serial-batch-selector.js?v=0.3.5"
	],
}

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "surgishoperpnext/public/scss/website"

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
# app_include_icons = "surgishoperpnext/public/icons.svg"

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
# 	"methods": "surgishoperpnext.utils.jinja_methods",
# 	"filters": "surgishoperpnext.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "surgishoperpnext.install.before_install"
# after_install = "surgishoperpnext.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "surgishoperpnext.uninstall.before_uninstall"
# after_uninstall = "surgishoperpnext.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "surgishoperpnext.utils.before_app_install"
# after_app_install = "surgishoperpnext.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "surgishoperpnext.utils.before_app_uninstall"
# after_app_uninstall = "surgishoperpnext.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "surgishoperpnext.notifications.get_notification_config"

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
# Hook on document methods and events for batch expiry override

# List of doctypes to apply overrides to
transaction_doctypes = [
    "Purchase Receipt",
    "Purchase Invoice",
    "Stock Entry",
    "Stock Reconciliation",
    "Sales Invoice",
    "Delivery Note"
]

# Common events and their override functions
override_events = {
    "before_validate": "surgishoperpnext.surgishoperpnext.overrides.stock_controller.disable_batch_expiry_validation",
    "after_insert": "surgishoperpnext.surgishoperpnext.overrides.stock_controller.restore_batch_expiry_validation",
    "on_cancel": "surgishoperpnext.surgishoperpnext.overrides.stock_controller.restore_batch_expiry_validation"
}

# Dynamically build doc_events dict
doc_events = {
    doctype: override_events.copy() for doctype in transaction_doctypes
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"surgishoperpnext.tasks.all"
# 	],
# 	"daily": [
# 		"surgishoperpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"surgishoperpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"surgishoperpnext.tasks.weekly"
# 	],
# 	"monthly": [
# 		"surgishoperpnext.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "surgishoperpnext.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.desktop.get_desktop_page": "surgishoperpnext.surgishoperpnext.overrides.desktop.get_desktop_page"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "surgishoperpnext.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["surgishoperpnext.utils.before_request"]
# after_request = ["surgishoperpnext.utils.after_request"]

# Job Events
# ----------
# before_job = ["surgishoperpnext.utils.before_job"]
# after_job = ["surgishoperpnext.utils.after_job"]

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
# 	"surgishoperpnext.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

