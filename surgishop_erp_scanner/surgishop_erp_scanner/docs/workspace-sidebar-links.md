# Adding Workspace Sidebar Links in ERPNext v16

This document explains how to programmatically add sidebar links to workspaces in ERPNext v16.

## Key Discovery: v16 Uses "Workspace Sidebar" DocType

**Important:** In ERPNext v16, the left sidebar is **NOT** controlled by the Workspace's links/shortcuts tables. It is controlled by a **completely separate DocType** called **"Workspace Sidebar"**.

## Understanding v16 Workspace Structure

| Component | DocType | Purpose |
|-----------|---------|---------|
| **Sidebar (left panel)** | `Workspace Sidebar` | Navigation links in the left sidebar |
| **Tiles (main area)** | `Workspace` → `shortcuts` table | Quick access shortcut tiles |
| **Link Cards** | `Workspace` → `links` table | Grouped card sections |
| **Content Layout** | `Workspace` → `content` JSON | Visual layout definition |

## Workspace Sidebar DocType Structure

```json
{
  "doctype": "Workspace Sidebar",
  "name": "YourWorkspaceName",
  "title": "Your Workspace Title",
  "module": "Your Module Name",
  "header_icon": "setting",
  "items": [
    {
      "type": "Link",
      "label": "Home",
      "link_to": "YourWorkspaceName",
      "link_type": "Workspace",
      "icon": "home",
      "child": 0,
      "collapsible": 1,
      "indent": 0,
      "keep_closed": 0,
      "show_arrow": 0
    },
    {
      "type": "Link",
      "label": "Your DocType",
      "link_to": "Your DocType",
      "link_type": "DocType",
      "icon": "setting",
      "child": 0,
      "collapsible": 1,
      "indent": 0,
      "keep_closed": 0,
      "show_arrow": 0
    }
  ]
}
```

### Item Properties

| Property | Description |
|----------|-------------|
| `type` | Usually `"Link"` or `"Section Break"` |
| `label` | Display text in sidebar |
| `link_to` | Target DocType, Report, or Workspace name |
| `link_type` | `"DocType"`, `"Report"`, `"Workspace"`, or `"Dashboard"` |
| `icon` | Lucide icon name (optional) |
| `child` | `0` for top-level, `1` for nested under a Section Break |
| `indent` | Indentation level |
| `collapsible` | Whether the section can collapse |
| `keep_closed` | Whether to start collapsed |

## Manual Method (via Fixture)

Create a JSON fixture file in your app:

```
your_app/workspace_sidebar/your_workspace.json
```

```json
{
  "doctype": "Workspace Sidebar",
  "name": "Your Workspace",
  "title": "Your Workspace",
  "module": "Your Module",
  "header_icon": "setting",
  "items": [
    {
      "type": "Link",
      "label": "Your Settings",
      "link_to": "Your Settings",
      "link_type": "DocType",
      "child": 0,
      "collapsible": 1,
      "indent": 0,
      "keep_closed": 0,
      "show_arrow": 0
    }
  ]
}
```

Then add to your `hooks.py`:

```python
fixtures = [
    {
        "doctype": "Workspace Sidebar",
        "filters": [["module", "=", "Your Module"]]
    }
]
```

## Programmatic Method (via after_migrate hook)

### Step 1: Create the hook function

```python
import frappe

def add_sidebar_link():
    """Add a link to an existing Workspace Sidebar."""
    try:
        sidebar_name = 'YourWorkspaceName'
        target_link = 'Your DocType'

        # Check if Workspace Sidebar exists
        if frappe.db.exists('Workspace Sidebar', sidebar_name):
            sidebar = frappe.get_doc('Workspace Sidebar', sidebar_name)

            # Check if link already exists
            existing_links = [item.get('link_to') for item in sidebar.items or []]
            if target_link in existing_links:
                return  # Already exists

            # Add the new link
            sidebar.append('items', {
                'type': 'Link',
                'label': 'Your Label',
                'link_to': target_link,
                'link_type': 'DocType',
                'child': 0,
                'collapsible': 1,
                'indent': 0,
                'keep_closed': 0,
                'show_arrow': 0,
            })

            sidebar.flags.ignore_permissions = True
            sidebar.save()

        else:
            # Create new Workspace Sidebar
            sidebar = frappe.get_doc({
                'doctype': 'Workspace Sidebar',
                'name': sidebar_name,
                'title': 'Your Title',
                'module': 'Your Module',
                'header_icon': 'setting',
                'items': [
                    {
                        'type': 'Link',
                        'label': 'Home',
                        'link_to': sidebar_name,
                        'link_type': 'Workspace',
                        'icon': 'home',
                        'child': 0,
                        'collapsible': 1,
                        'indent': 0,
                        'keep_closed': 0,
                        'show_arrow': 0,
                    },
                    {
                        'type': 'Link',
                        'label': 'Your Label',
                        'link_to': target_link,
                        'link_type': 'DocType',
                        'child': 0,
                        'collapsible': 1,
                        'indent': 0,
                        'keep_closed': 0,
                        'show_arrow': 0,
                    },
                ]
            })

            sidebar.flags.ignore_permissions = True
            sidebar.insert()

        frappe.db.commit()
        frappe.clear_cache(doctype='Workspace Sidebar')

    except Exception:
        frappe.log_error(
            title='Workspace Sidebar update failed',
            message=frappe.get_traceback(),
        )
```

### Step 2: Register the hook in hooks.py

```python
after_migrate = [
    "your_app.your_module.workspace_setup.add_sidebar_link"
]
```

### Step 3: Run migrate

```bash
bench --site yoursite migrate
```

## Adding Sections (Collapsible Groups)

To create a collapsible section with nested links:

```python
sidebar.append('items', {
    'type': 'Section Break',
    'label': 'Reports',
    'icon': 'notepad-text',
    'indent': 1,
    'keep_closed': 1,  # Start collapsed
    'child': 0,
    'collapsible': 1,
    'show_arrow': 0,
})

# Add child links (note child=1)
sidebar.append('items', {
    'type': 'Link',
    'label': 'My Report',
    'link_to': 'My Report',
    'link_type': 'Report',
    'child': 1,  # Nested under the section
    'collapsible': 1,
    'indent': 0,
    'keep_closed': 0,
    'show_arrow': 0,
})
```

## What Doesn't Work (Common Mistakes)

❌ **Adding to Workspace's `links` child table** - This controls Link Cards, NOT sidebar

❌ **Adding to Workspace's `shortcuts` child table** - This controls tiles, NOT sidebar

❌ **Adding blocks to Workspace's `content` JSON** - This controls layout, NOT sidebar

✅ **Creating/updating Workspace Sidebar doctype** - This is the correct approach!

## Debugging

Check if a Workspace Sidebar exists:

```python
import frappe
print(frappe.db.exists('Workspace Sidebar', 'YourWorkspaceName'))

# List all workspace sidebars
print(frappe.get_all('Workspace Sidebar', pluck='name'))
```

Inspect an existing sidebar:

```python
sidebar = frappe.get_doc('Workspace Sidebar', 'Stock')
for item in sidebar.items:
    print(f"{item.label} -> {item.link_to} ({item.link_type})")
```

## Reference Implementation

See `surgishop_erp_scanner/workspace_setup.py` for a complete working example.

## ERPNext Source Reference

ERPNext stores its Workspace Sidebar definitions in:
```
erpnext/workspace_sidebar/*.json
```

These files are great examples of the expected structure.
