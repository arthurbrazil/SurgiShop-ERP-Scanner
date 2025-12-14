# SurgiShop ERP Scanner

Custom Frappe app for SurgiShop with ERPNext modifications.

## Features

### GS1 Barcode Scanning

Advanced barcode scanning with GS1-128 support for medical devices and pharmaceuticals.

#### Features:

- **GS1 Parser** - Parses GS1 barcodes extracting GTIN (01), Expiry (17), Lot (10), Serial (21), etc.
- **Automatic Batch Creation** - Creates batches from scanned GS1 data with proper expiry dates
- **Smart Row Matching** - Same item+batch+warehouse increments qty; different creates new row
- **Warehouse Scanning** - Scan warehouse barcodes to set target warehouse
- **Audio Feedback** - Success/error sounds for scan confirmation
- **New Line Trigger** - Scan a special barcode to force next item onto a new line

#### Supported Documents:

- Stock Entry
- Purchase Order
- Purchase Receipt
- Purchase Invoice
- Sales Invoice
- Delivery Note
- Stock Reconciliation

#### Trigger Barcodes:

Configure special barcodes that trigger actions on the next scan:

| Trigger                        | Description                                               |
| ------------------------------ | --------------------------------------------------------- |
| **New Line Trigger**           | Forces next item onto a new row (vs incrementing qty)     |
| **Condition Trigger**          | Prompts for condition, applies to next scanned item       |
| **Quantity Trigger**           | Prompts for quantity on next scan                         |
| **Delete Row Trigger**         | Removes the last scanned row from the items table         |

### SurgiShop Settings

This app includes a settings page accessible from the desk sidebar under **SurgiShop > SurgiShop Settings**.

#### Scanner Settings:

| Setting                    | Default    | Description                                              |
| -------------------------- | ---------- | -------------------------------------------------------- |
| **Enable Scan Sounds**     | ✅ Enabled | Play audio feedback on scan success/failure              |
| **Prompt for Quantity**    | ❌ Disabled| Ask for quantity on every scan                           |
| **Default Scan Quantity**  | 1          | Quantity to add per scan (when not prompting)            |
| **Auto-Create Batches**    | ✅ Enabled | Create batch if it doesn't exist (vs showing error)      |

#### Trigger Barcodes:

| Setting                        | Default | Description                                        |
| ------------------------------ | ------- | -------------------------------------------------- |
| **New Line Trigger Barcode**   | (empty) | Barcode that forces next item onto new row         |
| **Condition Trigger Barcode**  | (empty) | Barcode that prompts for condition on next scan    |
| **Quantity Trigger Barcode**   | (empty) | Barcode that prompts for quantity on next scan     |
| **Delete Row Trigger Barcode** | (empty) | Barcode that deletes the last scanned row          |

#### Batch Settings:

| Setting                    | Default    | Description                                              |
| -------------------------- | ---------- | -------------------------------------------------------- |
| **Warn on Expiry Mismatch**| ✅ Enabled | Alert if scanned expiry differs from existing batch      |
| **Update Missing Expiry**  | ✅ Enabled | Update batch expiry from scan if batch has none          |
| **Strict GTIN Validation** | ❌ Disabled| Require exact GTIN match in Item Barcodes                |

#### Batch Expiry Settings:

| Setting                              | Default     | Description                                                         |
| ------------------------------------ | ----------- | ------------------------------------------------------------------- |
| **Allow Expired Batches on Inbound** | ✅ Enabled  | Master toggle for allowing expired batches on inbound transactions  |
| **Skip All Batch Expiry Validation** | ❌ Disabled | WARNING: Completely disables expiry validation for all transactions |
| **Purchase Receipt**                 | ✅ Enabled  | Allow expired batches on Purchase Receipt documents                 |
| **Purchase Invoice**                 | ✅ Enabled  | Allow expired batches on Purchase Invoice documents                 |
| **Stock Entry (Material Receipt)**   | ✅ Enabled  | Allow expired batches on Stock Entry with Material Receipt purpose  |
| **Stock Reconciliation**             | ✅ Enabled  | Allow expired batches on Stock Reconciliation documents             |
| **Sales Returns**                    | ✅ Enabled  | Allow expired batches on Sales Returns                              |

### Condition Tracking

Track the condition of items on Purchase Receipts and propagate to Stock Ledger Entries.

#### Features:

- **Condition field on Purchase Receipt Items** - Select from configurable options (e.g., "<3mo Dating", "Blister Damage", "Expired", etc.)
- **Automatic propagation to Stock Ledger Entry** - Condition is copied on submit
- **Configurable options** - Manage condition options via **SurgiShop Condition Settings**

#### How to configure:

1. Go to **SurgiShop > SurgiShop Condition Settings**
2. Add/remove condition options as needed
3. Save - options will be synced to the Purchase Receipt Item and Stock Ledger Entry fields

### Stock Controller Override

This app overrides the default ERPNext StockController behavior to allow expired products to be received into the system for inbound transactions, based on the settings configured above.

#### What it does:

- **Allows expired products** to be received through inbound transactions (Purchase Receipt, Purchase Invoice, Stock Entry with Material Receipt, etc.) when enabled in settings
- **Maintains expiry validation** for outbound transactions to prevent selling expired products
- **Preserves all other stock validation** functionality

#### Supported Inbound Transactions:

- Purchase Receipt
- Purchase Invoice
- Stock Entry (Material Receipt purpose)
- Stock Entry (Material Transfer with only target warehouse)
- Stock Reconciliation (positive quantities)
- Sales Returns (Sales Invoice/Delivery Note with is_return=True)

#### Outbound Transactions (expiry validation still enforced):

- Purchase Returns
- Stock Entry (Material Issue)
- Stock Entry (Material Transfer with both source and target warehouses)
- Sales Invoice (normal sales)
- Delivery Note (normal deliveries)

## Installation

1. Install the app in your Frappe/ERPNext instance:

   ```bash
   bench get-app https://github.com/arthurbrazil/SurgiShop-ERP-Scanner.git
   bench install-app surgishop_erp_scanner
   ```

2. Run migrations to create the settings DocType:

   ```bash
   bench migrate
   ```

3. Access settings from **SurgiShop > SurgiShop Settings** in the desk sidebar.

## Testing

Run the test suite to verify the implementation:

```bash
bench run-tests --app surgishop_erp_scanner
```

## Technical Details

### File Structure

```
surgishop_erp_scanner/
├── hooks.py                           # App hooks and doc_events
├── fixtures/
│   └── custom_field.json              # Condition field fixtures
├── public/
│   └── js/
│       ├── gs1-utils.js               # GS1 barcode parser
│       ├── custom-barcode-scanner.js  # Scanner override for forms
│       └── custom-serial-batch-selector.js  # Serial/batch dialog enhancements
├── surgishop_erp_scanner/
│   ├── api/
│   │   ├── gs1_parser.py              # GS1 parsing and batch creation API
│   │   └── barcode.py                 # Barcode lookup API
│   ├── doctype/
│   │   ├── surgishop_settings/        # Scanner + batch expiry settings
│   │   ├── surgishop_condition_settings/  # Condition options settings
│   │   └── surgishop_condition_option/    # Condition option child table
│   ├── overrides/
│   │   ├── stock_controller.py        # Batch expiry validation override
│   │   └── condition_tracking.py      # PR → SLE condition sync
│   ├── docs/
│   │   └── workspace-sidebar-links.md # v16 workspace documentation
│   ├── condition_options.py           # Condition options sync logic
│   ├── workspace_setup.py             # Workspace shortcut injection
│   └── install.py                     # Post-install setup
```

### How It Works

1. The override is registered in `hooks.py` using the `doc_events` hook
2. When stock documents are validated, `validate_serialized_batch_with_expired_override()` is called
3. The function checks `SurgiShop Settings` to determine if expired batches should be allowed
4. For inbound transactions with settings enabled, batch expiry validation is skipped
5. For outbound transactions, standard ERPNext batch expiry validation is enforced

This approach uses document event hooks instead of class inheritance, making it more resilient to ERPNext updates.

## Developer Documentation

### Adding Workspace Sidebar Links (v16)

See [docs/workspace-sidebar-links.md](docs/workspace-sidebar-links.md) for detailed documentation on how to programmatically add sidebar links to workspaces in ERPNext v16.

**Key discovery:** In v16, the sidebar is controlled by a **completely separate DocType** called `Workspace Sidebar`, NOT the Workspace's links/shortcuts tables!

Key points:

- Sidebar links come from the **Workspace Sidebar** DocType
- Workspace `shortcuts` table controls **tiles** (not sidebar)
- Workspace `links` table controls **link cards** (not sidebar)
- Use `after_migrate` hooks for automatic injection
- See `erpnext/workspace_sidebar/*.json` for examples

## License

MIT License
