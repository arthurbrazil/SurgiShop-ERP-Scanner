## SurgiShopERPNext

Custom Frappe/ERPNext app for SurgiShop with configurable batch expiry validation overrides.

### Features

- **Configurable Settings Page** - Toggle batch expiry overrides from the desk UI
- **Allow Expired Batches on Inbound** - Receive expired products into inventory
- **Granular Control** - Enable/disable per document type (Purchase Receipt, Stock Entry, etc.)
- **Outbound Protection** - Maintains expiry validation on sales to prevent selling expired products

### Quick Start

```bash
# Install the app
bench get-app surgishoperpnext
bench install-app surgishoperpnext
bench migrate

# Access settings
# Navigate to: SurgiShop > SurgiShop Settings
```

### Settings

Access **SurgiShop > SurgiShop Settings** from the desk sidebar to configure:

| Setting | Description |
|---------|-------------|
| Allow Expired Batches on Inbound | Master toggle for inbound transactions |
| Skip All Batch Expiry Validation | Disable all expiry checks (use with caution) |
| Purchase Receipt | Allow on Purchase Receipt documents |
| Purchase Invoice | Allow on Purchase Invoice documents |
| Stock Entry (Material Receipt) | Allow on Stock Entry receipts |
| Stock Reconciliation | Allow on Stock Reconciliation |
| Sales Returns | Allow on Sales Returns |

### Documentation

See [surgishoperpnext/surgishoperpnext/README.md](surgishoperpnext/surgishoperpnext/README.md) for detailed documentation.

### License

MIT
