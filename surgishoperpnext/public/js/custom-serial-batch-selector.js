// Custom Serial Batch Selector - Redone Version

console.log("🏥 Custom Serial Batch Selector loaded (redone version)");

// Patch Original Constructor
if (erpnext.SerialBatchPackageSelector) {
  // Patch constructor
  const originalConstructor =
    erpnext.SerialBatchPackageSelector.prototype.constructor;
  erpnext.SerialBatchPackageSelector.prototype.constructor = function (opts) {
    console.log("🔍 DIAGNOSTIC - SerialBatchPackageSelector constructor called with opts:", {
      hasOpts: !!opts,
      hasItem: opts && !!opts.item,
      item: opts && opts.item,
      callback: opts && opts.callback,
      frm: opts && opts.frm,
      bundleId: opts && opts.bundle_id,
      serialAndBatchBundle: opts && opts.item && opts.item.serial_and_batch_bundle,
      fullOpts: opts
    });
    
    // Check localStorage and sessionStorage for cached values
    console.log("🔍 DIAGNOSTIC - Checking browser storage:", {
      localStorage: Object.keys(localStorage).filter(k => k.includes('batch') || k.includes('scan')),
      sessionStorage: Object.keys(sessionStorage).filter(k => k.includes('batch') || k.includes('scan'))
    });
    
    if (opts && opts.item) {
      this.qty = opts.item.qty;
    } else {
      this.qty = 0;
      console.log("🏥 Patched: No item - set qty to 0");
    }
    originalConstructor.apply(this, arguments);
  };

  // Patch make to add custom scan handler
  const originalMake = erpnext.SerialBatchPackageSelector.prototype.make;
  erpnext.SerialBatchPackageSelector.prototype.make = function () {
    console.log("🔍 DIAGNOSTIC - BEFORE originalMake called");
    console.log("🔍 DIAGNOSTIC - This object state:", {
      item: this.item,
      bundle_id: this.bundle_id,
      frm: this.frm ? this.frm.doctype : null,
      itemCode: this.item ? this.item.item_code : null
    });
    
    // Intercept frappe.db.get_value to see what ERPNext is fetching
    const originalGetValue = frappe.db.get_value;
    frappe.db.get_value = function(...args) {
      console.log("🔍 DIAGNOSTIC - frappe.db.get_value called:", args);
      return originalGetValue.apply(this, args);
    };
    
    originalMake.call(this);
    
    // Restore original get_value after a short delay
    setTimeout(() => {
      frappe.db.get_value = originalGetValue;
    }, 2000);
    
    console.log("🔍 DIAGNOSTIC - AFTER originalMake called");

    console.log("🏥 Dialog box opened!");

    if (this.item && this.item.item_code) {
      const newTitle = `${this.dialog.title} - Item: ${this.item.item_code}`;
      this.dialog.set_title(newTitle);
      console.log("🏥 Updated title to:", newTitle);
    }

    // Fix grid metadata to prevent errors when deleting rows
    const entriesGrid = this.dialog.fields_dict.entries.grid;
    if (entriesGrid) {
      // Initialize meta object if it doesn't exist
      if (!entriesGrid.meta) {
        entriesGrid.meta = {};
      }
      // Set editable_grid property
      entriesGrid.meta.editable_grid = 1;
      entriesGrid.meta.fields = entriesGrid.df.fields || [];
      console.log("🏥 Fixed grid metadata for row deletion", entriesGrid.meta);
    }

    // Add custom onchange to scan_batch_no
    const scanField = this.dialog.fields_dict.scan_batch_no;
    if (scanField) {
      // DIAGNOSTIC LOGGING - Check initial state
      const initialValue = scanField.get_value();
      const fieldDef = scanField.df;
      console.log("🔍 DIAGNOSTIC - scan_batch_no field state at dialog open:", {
        initialValue: initialValue,
        hasValue: !!initialValue,
        fieldName: fieldDef.fieldname,
        fieldType: fieldDef.fieldtype,
        defaultValue: fieldDef.default,
        hasOnchangeAlready: !!fieldDef.onchange,
        fieldObject: scanField
      });
      
      // Use a flag to ignore the first automatic trigger
      let isFirstLoad = true;
      
      // Store original onchange if it exists
      const originalOnchange = fieldDef.onchange;
      if (originalOnchange) {
        console.log("🔍 DIAGNOSTIC - scan_batch_no already has an onchange handler!");
      }
      
      // Intercept set_value to see when and how it's being called
      const originalSetValue = scanField.set_value.bind(scanField);
      scanField.set_value = function(value) {
        console.log("🔍 DIAGNOSTIC - set_value called on scan_batch_no:", {
          newValue: value,
          stackTrace: new Error().stack
        });
        return originalSetValue(value);
      };
      
      scanField.df.onchange = () => {
        const currentValue = scanField.get_value();
        console.log("🔍 DIAGNOSTIC - onchange triggered:", {
          isFirstLoad: isFirstLoad,
          currentValue: currentValue,
          valueLength: currentValue ? currentValue.length : 0
        });
        
        // Ignore the first onchange trigger (happens when dialog loads with existing value)
        if (isFirstLoad) {
          isFirstLoad = false;
          scanField.set_value("");
          console.log("🏥 Ignored first onchange trigger and cleared scan field");
          return;
        }
        
        const scannedValue = scanField.get_value();
        if (!scannedValue) return;

        // Parse GS1
        console.log("🔍 DIAGNOSTIC - About to parse GS1, stack trace:", new Error().stack);
        const parsed = window.surgishop.GS1Parser.parse(scannedValue);
        if (!parsed || !parsed.gtin || !parsed.lot || !parsed.expiry) {
          frappe.show_alert({
            message: __("Invalid GS1 barcode format"),
            indicator: 'red'
          }, 5);
          scanField.set_value("");
          frappe.utils.play_sound("error");
          return;
        }

        // Get item_code from GTIN
        frappe.db
          .get_doc("Item", this.item.item_code)
          .then((doc) => {
            const hasGtin =
              doc.barcodes &&
              doc.barcodes.some((b) => b.barcode === parsed.gtin);
            if (!hasGtin) {
              frappe.show_alert({
                message: __(
                  "GTIN " +
                    parsed.gtin +
                    " does not match the barcodes for item: " +
                    this.item.item_code
                ),
                indicator: 'red'
              }, 5);
              scanField.set_value("");
              frappe.utils.play_sound("error");
              return;
            }

            // Proceed with batch creation...
            // Format batch_no
            const formattedBatchNo = `${this.item.item_code}-${parsed.lot}`;

            // Call API
            frappe.call({
              method:
                "surgishoperpnext.surgishoperpnext.api.gs1_parser.parse_gs1_and_get_batch",
              args: {
                gtin: parsed.gtin,
                expiry: parsed.expiry,
                lot: parsed.lot,
                item_code: this.item.item_code,
              },
              callback: (res) => {
                if (!res.message || res.message.error) {
                  frappe.show_alert({
                    message: __(
                      "Error creating or getting batch: " +
                        (res.message.error || "Unknown error")
                    ),
                    indicator: 'red'
                  }, 5);
                  scanField.set_value("");
                  frappe.utils.play_sound("error");
                  return;
                }

                const batch = res.message.batch;
                const batchExpiry = res.message.batch_expiry_date;

                // Format scanned expiry to 'YYYY-MM-DD'
                const scannedExpiry =
                  "20" +
                  parsed.expiry.slice(0, 2) +
                  "-" +
                  parsed.expiry.slice(2, 4) +
                  "-" +
                  parsed.expiry.slice(4, 6);

                // Validate expiry matches scanned
                if (batchExpiry !== scannedExpiry) {
                  frappe.show_alert({
                    message: __("Batch expiry does not match scanned expiry"),
                    indicator: 'orange'
                  }, 5);
                  scanField.set_value("");
                  frappe.utils.play_sound("error");
                  return;
                }

				// Add to grid data directly (dialog grids work differently than form child tables)
				const grid = this.dialog.fields_dict.entries.grid;
				
				// Get the grid's data array
				const gridData = grid.get_data ? grid.get_data() : [];
				
				// Check if batch already exists in the grid
				const existingRow = gridData.find(row => row.batch_no === batch);
				
				if (existingRow) {
					// Increment quantity if batch already exists
					existingRow.qty = (existingRow.qty || 0) + 1;
					console.log(`🏥 Incremented quantity for batch ${batch} to ${existingRow.qty}`);
					frappe.show_alert({
						message: __(`Batch ${batch}: Qty increased to ${existingRow.qty}`),
						indicator: 'green'
					}, 3);
				} else {
					// Create a new row object if batch doesn't exist
					const newRow = {
						batch_no: batch,
						qty: 1,
						expiry_date: batchExpiry
					};
					
					// Add the new row to the data
					gridData.push(newRow);
					
					console.log("🏥 Successfully added new batch row:", newRow);
					frappe.show_alert({
						message: __(`Batch ${batch} added with qty 1`),
						indicator: 'green'
					}, 3);
				}
				
				// Set the grid data and refresh
				if (grid.df && grid.df.data) {
					grid.df.data = gridData;
				}
				
				grid.refresh();
				
				console.log("🏥 Current grid data:", gridData);
				
				scanField.set_value("");
				frappe.utils.play_sound("submit"); // Play success sound
              },
            });
          })
          .catch((err) => {
            frappe.show_alert({
              message: __("Error fetching item details: " + err.message),
              indicator: 'red'
            }, 5);
            scanField.set_value("");
            frappe.utils.play_sound("error");
          });
      };
    }

    console.log("🏥 Added custom GS1 scan handler to scan_batch_no");
  };

  console.log("🏥 Patches applied successfully");
}

// Patch get_dialog_table_fields to add expiry_date column in correct order
const originalGetFields =
  erpnext.SerialBatchPackageSelector.prototype.get_dialog_table_fields;
erpnext.SerialBatchPackageSelector.prototype.get_dialog_table_fields =
  function () {
    const originalFields = originalGetFields.call(this);
    const expiryField = {
      fieldtype: "Date",
      fieldname: "expiry_date",
      label: __("Expiry Date"),
      in_list_view: 1,
      read_only: 1,
    };
    originalFields.splice(1, 0, expiryField); // Insert after batch_no (index 0), before qty (now index 2)

    // Add onchange to batch_no for auto-fetch
    const batchField = originalFields.find((f) => f.fieldname === "batch_no");
    if (batchField) {
      batchField.onchange = function () {
        const batch_no = this.value;
        if (batch_no) {
          frappe.db.get_value("Batch", batch_no, "expiry_date", (r) => {
            this.grid_row.on_grid_fields_dict.expiry_date.set_value(
              r.expiry_date
            );
          });
        } else {
          this.grid_row.on_grid_fields_dict.expiry_date.set_value(null);
        }
      };
    }

    return originalFields;
  };

// Patch set_data to fetch expiry dates for initial data
const originalSetData = erpnext.SerialBatchPackageSelector.prototype.set_data;
erpnext.SerialBatchPackageSelector.prototype.set_data = function (data) {
  const promises = data.map((d) => {
    if (d.batch_no) {
      return new Promise((resolve) => {
        frappe.db.get_value("Batch", d.batch_no, "expiry_date", (r) => {
          d.expiry_date = r.expiry_date;
          resolve();
        });
      });
    }
    return Promise.resolve();
  });

  Promise.all(promises).then(() => {
    originalSetData.call(this, data);
  });
};

console.log(
  "🏥 Added expiry date column with order, auto-fetch on change, and initial data handling"
);

console.log("🏥 Proxy wrapper applied - error-proof!");

// Safe DOM Modification for Dialog Title

console.log("🏥 Safe Dialog Modifier Loaded");

// Global storage for item code from clicked row
let currentItemCode = "";

// Detect button clicks and store item code
$(document).on(
  "click",
  '[data-label="Add Serial / Batch No"], .btn[data-fieldname*="serial_and_batch_bundle"]',
  function (e) {
    const $btn = $(this);
    const $row = $btn.closest(".grid-row");
    if ($row.length) {
      currentItemCode =
        $row
          .find('[data-fieldname="item_code"] .grid-static-col')
          .text()
          .trim() || "";
      console.log("🏥 Button clicked - Stored item code:", currentItemCode);
    }
  }
);

// Observe for dialog opening and modify title
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    mutation.addedNodes.forEach((node) => {
      if (node.nodeType === 1 && node.classList.contains("modal-dialog")) {
        const titleElem = node.querySelector(".modal-title");
        if (
          titleElem &&
          titleElem.textContent.includes("Add Batch Nos") &&
          currentItemCode
        ) {
          titleElem.textContent += ` - Item: ${currentItemCode}`;
          console.log(
            "🏥 Dialog opened and title updated to:",
            titleElem.textContent
          );
          currentItemCode = ""; // Reset
        }
      }
    });
  });
});
observer.observe(document.body, { childList: true, subtree: true });

console.log("🏥 Observer setup complete - waiting for dialog");
