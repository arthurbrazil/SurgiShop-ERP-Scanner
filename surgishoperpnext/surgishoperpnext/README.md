# SurgiShopERPNext

Custom Frappe app for SurgiShop with ERPNext modifications.

## Features

### SurgiShop Settings

This app includes a settings page accessible from the desk sidebar under **SurgiShop > SurgiShop Settings**.

#### Settings Options:

| Setting | Default | Description |
|---------|---------|-------------|
| **Allow Expired Batches on Inbound** | ✅ Enabled | Master toggle for allowing expired batches on inbound transactions |
| **Skip All Batch Expiry Validation** | ❌ Disabled | WARNING: Completely disables expiry validation for all transactions |
| **Purchase Receipt** | ✅ Enabled | Allow expired batches on Purchase Receipt documents |
| **Purchase Invoice** | ✅ Enabled | Allow expired batches on Purchase Invoice documents |
| **Stock Entry (Material Receipt)** | ✅ Enabled | Allow expired batches on Stock Entry with Material Receipt purpose |
| **Stock Reconciliation** | ✅ Enabled | Allow expired batches on Stock Reconciliation documents |
| **Sales Returns** | ✅ Enabled | Allow expired batches on Sales Returns |

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
   bench get-app surgishoperpnext
   bench install-app surgishoperpnext
   ```

2. Run migrations to create the settings DocType:
   ```bash
   bench migrate
   ```

3. Access settings from **SurgiShop > SurgiShop Settings** in the desk sidebar.

## Testing

Run the test suite to verify the implementation:

```bash
bench run-tests --app surgishoperpnext
```

## Technical Details

### File Structure

```
surgishoperpnext/
├── hooks.py                           # App hooks and doc_events
├── surgishoperpnext/
│   ├── doctype/
│   │   └── surgishop_settings/        # Settings DocType
│   │       ├── surgishop_settings.json
│   │       └── surgishop_settings.py
│   ├── overrides/
│   │   └── stock_controller.py        # Batch expiry validation override
│   ├── workspace/
│   │   └── surgishop/                 # Desk sidebar workspace
│   │       └── surgishop.json
│   └── install.py                     # Post-install setup
```

### How It Works

1. The override is registered in `hooks.py` using the `doc_events` hook
2. When stock documents are validated, `validate_serialized_batch_with_expired_override()` is called
3. The function checks `SurgiShop Settings` to determine if expired batches should be allowed
4. For inbound transactions with settings enabled, batch expiry validation is skipped
5. For outbound transactions, standard ERPNext batch expiry validation is enforced

This approach uses document event hooks instead of class inheritance, making it more resilient to ERPNext updates.

## License

MIT License
