# Adding Workspace Sidebar Links in ERPNext v16

This document explains how to programmatically add sidebar links to existing workspaces in ERPNext v16.

## Understanding v16 Workspace Structure

In ERPNext v16, workspaces have multiple components that control different parts of the UI:

| Component | Purpose | Where it appears |
|-----------|---------|------------------|
| **Links** (child table) | Sidebar navigation links | **Sidebar** (left panel) |
| **Shortcuts** (child table) | Quick access tiles | **Tiles** (main workspace area) |
| **Link Cards** (child table) | Grouped card links | Main workspace page (card sections) |
| **Content** (JSON field) | Visual layout definition | Controls rendering of shortcuts/cards |

**Important:** In v16:
- The **sidebar** is rendered from the **Links** table
- The **tiles** (shortcuts) in the main area come from the **Shortcuts** table AND the `content` JSON
- You may need to update ALL THREE for complete functionality

## Manual Method (via UI)

1. Navigate to the workspace page (e.g., `/desk/surgishop`)
2. Click **Edit** (bottom right)
3. Add a new **Shortcut**:
   - Type: `DocType`
   - Link To: `Your DocType Name`
   - Label: `Your Label`
4. Click **Save**

## Programmatic Method (via after_migrate hook)

### Step 1: Create the hook function

Create a file like `workspace_setup.py`:

```python
import json
import frappe

def add_shortcut_to_workspace():
    """
    Add a shortcut to an existing workspace.
    Runs after every migrate.
    """
    try:
        workspace_name = 'YourWorkspaceName'
        
        if not frappe.db.exists('Workspace', workspace_name):
            return
        
        ws = frappe.get_doc('Workspace', workspace_name)
        
        # Check if shortcut already exists in shortcuts table
        existing = [s.get('link_to') for s in ws.shortcuts or []]
        shortcut_exists = 'Your DocType Name' in existing
        
        # Check if shortcut exists in content JSON
        content = json.loads(ws.content or '[]')
        content_has_shortcut = any(
            block.get('type') == 'shortcut' and 
            block.get('data', {}).get('shortcut_name') == 'Your DocType Name'
            for block in content
        )
        
        if shortcut_exists and content_has_shortcut:
            return  # Already exists
        
        # Add to shortcuts table
        if not shortcut_exists:
            ws.append('shortcuts', {
                'label': 'Your Label',
                'link_to': 'Your DocType Name',
                'type': 'DocType',
            })
        
        # Add to content JSON
        if not content_has_shortcut:
            content.append({
                'id': 'unique_shortcut_id',
                'type': 'shortcut',
                'data': {
                    'shortcut_name': 'Your DocType Name',
                    'col': 4
                }
            })
            ws.content = json.dumps(content)
        
        # Fix mandatory fields if needed
        if not ws.get('type'):
            ws.type = 'Workspace'
        
        # Save with bypasses
        ws.flags.ignore_mandatory = True
        ws.flags.ignore_permissions = True
        ws.save()
        
        frappe.db.commit()
        frappe.clear_cache(doctype='Workspace')
        
    except Exception:
        frappe.log_error(
            title='Workspace update failed',
            message=frappe.get_traceback(),
        )
```

### Step 2: Register the hook in hooks.py

```python
after_migrate = [
    "your_app.your_module.workspace_setup.add_shortcut_to_workspace"
]
```

### Step 3: Run migrate

```bash
bench --site yoursite migrate
```

## Key Lessons Learned

1. **Shortcuts vs Link Cards**: The sidebar uses **Shortcuts**, not Link Cards
2. **Content JSON**: v16 may require BOTH the shortcuts table AND the content JSON to be updated
3. **Mandatory fields**: Some workspaces may be missing mandatory fields like `type`. Use `ws.flags.ignore_mandatory = True` when saving
4. **Caching**: Always call `frappe.clear_cache()` after updating workspaces
5. **Don't use Workspace fixtures for existing workspaces**: If users already have a workspace, creating one via fixtures will create a duplicate

## Cloning Existing Shortcuts

To match the exact structure of an existing shortcut, you can clone it:

```python
# Find existing shortcut in content JSON
template_block = None
for block in content:
    if block.get('type') == 'shortcut':
        data = block.get('data') or {}
        if data.get('shortcut_name') == 'Existing Shortcut Name':
            template_block = block
            break

if template_block:
    # Clone and modify
    new_block = json.loads(json.dumps(template_block))
    new_block['id'] = 'new_unique_id'
    new_block['data']['shortcut_name'] = 'New Shortcut Name'
    content.append(new_block)
```

## Debugging

Add print statements to see what's happening during migrate:

```python
print(f">>> Shortcuts: {[s.get('link_to') for s in ws.shortcuts]}")
print(f">>> Content: {ws.content}")
```

Check the Error Log in ERPNext for any logged errors:
- Press `Ctrl+K` → type "Error Log" → open it

## Reference Implementation

See `surgishop_erp_scanner/workspace_setup.py` for a complete working example.

