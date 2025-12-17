/**
 * SurgiShop ERP Scanner - Custom Barcode Scanner Override
 * Overrides ERPNext's default barcode scanning with custom functionality
 */

// Namespace for our custom code to avoid polluting the global scope
if (typeof window.surgishop === "undefined") {
  window.surgishop = {};
}

// Suppress ERPNext's internal DOM timing errors during barcode scanning
// These errors occur when ERPNext tries to refresh grid fields before DOM is ready
// The errors are harmless - values still get set correctly
window.addEventListener("unhandledrejection", (event) => {
  if (
    event.reason &&
    event.reason.message &&
    event.reason.message.includes("can't access property") &&
    event.reason.message.includes("parent")
  ) {
    // Suppress this specific ERPNext timing error
    event.preventDefault();
  }
});

// Scanner state flags
window.surgishop.forceNewRow = false;
window.surgishop.forcePromptQty = false;
window.surgishop.pendingCondition = null;

// Settings (will be loaded from SurgiShop Settings)
window.surgishop.settings = {
  enableScanSounds: true,
  promptForQuantity: false,
  defaultScanQuantity: 1,
  autoCreateBatches: true,
  disableSerialBatchSelector: true,
  newLineTriggerBarcode: null,
  conditionTriggerBarcode: null,
  quantityTriggerBarcode: null,
  deleteRowTriggerBarcode: null,
  warnOnExpiryMismatch: true,
  updateMissingExpiry: true,
  strictGtinValidation: false,
};

/**
 * Our custom scanner class.
 * All the logic for parsing and handling scans is contained here.
 */
surgishop.CustomBarcodeScanner = class CustomBarcodeScanner {
  constructor(opts) {
    this.frm = opts.frm;
    this.scan_field_name = opts.scan_field_name || "scan_barcode";
    this.scan_barcode_field = this.frm.fields_dict[this.scan_field_name];
    this.barcode_field = opts.barcode_field || "barcode";
    this.serial_no_field = opts.serial_no_field || "serial_no";
    this.batch_no_field = opts.batch_no_field || "batch_no";
    this.batch_expiry_date_field =
      opts.batch_expiry_date_field || "custom_expiration_date";
    this.uom_field = opts.uom_field || "uom";
    this.qty_field = opts.qty_field || "qty";
    this.warehouse_field = opts.warehouse_field || "warehouse";
    this.condition_field = opts.condition_field || "custom_condition";
    this.max_qty_field = opts.max_qty_field;
    this.dont_allow_new_row = opts.dont_allow_new_row;
    this.items_table_name = opts.items_table_name || "items";

    // Use settings for sounds
    const settings = window.surgishop.settings;
    this.enable_sounds = settings.enableScanSounds;
    this.success_sound = this.enable_sounds ? "submit" : null;
    this.fail_sound = this.enable_sounds ? "error" : null;

    // Use settings for quantity behavior
    this.prompt_qty = opts.prompt_qty || settings.promptForQuantity;
    this.default_qty = settings.defaultScanQuantity || 1;

    this.scan_api =
      opts.scan_api ||
      "surgishop_erp_scanner.surgishop_erp_scanner.api.barcode.scan_barcode";
    this.gs1_parser_api =
      "surgishop_erp_scanner.surgishop_erp_scanner.api.gs1_parser.parse_gs1_and_get_batch";
    this.has_last_scanned_warehouse = frappe.meta.has_field(
      this.frm.doctype,
      "last_scanned_warehouse"
    );
  }

  /**
   * Parses a GS1 string using the shared GS1Parser utility.
   * @param {string} gs1_string The raw scanned string
   * @returns {object|null} Parsed data {gtin, lot, expiry} or null if not matching
   */
  parse_gs1_string(gs1_string) {
    if (window.surgishop && window.surgishop.GS1Parser) {
      return window.surgishop.GS1Parser.parse(gs1_string);
    } else {
      return null;
    }
  }

  /**
   * Check if this is a special trigger barcode
   * @param {string} input The scanned barcode
   * @returns {boolean} True if this is a trigger barcode that was handled
   */
  check_trigger_barcode(input) {
    const settings = window.surgishop.settings;

    // New Line Trigger
    if (
      settings.newLineTriggerBarcode &&
      input === settings.newLineTriggerBarcode
    ) {
      window.surgishop.forceNewRow = true;
      this.show_alert(
        "New Line Mode: Next scan will create a new row",
        "orange",
        3
      );
      this.play_success_sound();
      return true;
    }

    // Condition Trigger
    if (
      settings.conditionTriggerBarcode &&
      input === settings.conditionTriggerBarcode
    ) {
      this.prompt_for_condition();
      return true;
    }

    // Quantity Trigger
    if (
      settings.quantityTriggerBarcode &&
      input === settings.quantityTriggerBarcode
    ) {
      window.surgishop.forcePromptQty = true;
      this.show_alert(
        "Quantity Mode: Next scan will prompt for quantity",
        "blue",
        3
      );
      this.play_success_sound();
      return true;
    }

    // Delete Row Trigger
    if (
      settings.deleteRowTriggerBarcode &&
      input === settings.deleteRowTriggerBarcode
    ) {
      this.delete_last_row();
      return true;
    }

    return false;
  }

  /**
   * Prompt for condition selection with touch-friendly dialog
   */
  prompt_for_condition() {
    // Fetch condition options via custom API (bypasses permission issues)
    frappe.call({
      method:
        "surgishop_erp_scanner.surgishop_erp_scanner.api.barcode.get_condition_options",
      callback: (r) => {
        let options = r && r.message ? r.message : [];

        if (options.length === 0) {
          this.show_alert(
            "No condition options configured. Please add options in SurgiShop Condition Settings.",
            "orange",
            5
          );
          this.play_fail_sound();
          return;
        }

        this.show_touch_condition_dialog(options);
      },
      error: () => {
        this.show_alert("Failed to load condition options.", "red", 5);
        this.play_fail_sound();
      },
    });
  }

  /**
   * Show touch-friendly condition dialog (tap to select and apply)
   * @param {Array} options - List of condition options
   */
  show_touch_condition_dialog(options) {
    const self = this;

    // Create custom dialog with large touch-friendly buttons
    const dialog = new frappe.ui.Dialog({
      title: "Tap a Condition",
      size: "large",
      fields: [
        {
          fieldtype: "HTML",
          fieldname: "condition_buttons",
          options: `
            <style>
              .condition-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 12px;
                padding: 10px 0;
                max-height: 70vh;
                overflow-y: auto;
              }
              .condition-btn {
                padding: 20px 16px;
                font-size: 16px;
                font-weight: 500;
                border: 2px solid var(--border-color);
                border-radius: 8px;
                background: var(--bg-color);
                color: var(--text-color);
                cursor: pointer;
                transition: all 0.15s ease;
                text-align: center;
                min-height: 70px;
                display: flex;
                align-items: center;
                justify-content: center;
                user-select: none;
                -webkit-tap-highlight-color: transparent;
              }
              .condition-btn:hover {
                border-color: var(--primary-color);
                background: var(--control-bg);
              }
              .condition-btn:active {
                transform: scale(0.96);
                background: var(--primary-color);
                border-color: var(--primary-color);
                color: white;
              }
              @media (max-width: 768px) {
                .condition-grid {
                  grid-template-columns: 1fr;
                }
                .condition-btn {
                  padding: 24px 16px;
                  font-size: 18px;
                  min-height: 80px;
                }
              }
            </style>
            <div class="condition-grid">
              ${options
                .map(
                  (opt) => `
                <button type="button" class="condition-btn" data-condition="${opt.replace(
                  /"/g,
                  "&quot;"
                )}">
                  ${opt}
                </button>
              `
                )
                .join("")}
            </div>
          `,
        },
      ],
    });

    // Hide the default footer buttons
    dialog.$wrapper.find(".modal-footer").hide();

    dialog.show();

    // Tap to select AND apply immediately
    dialog.$wrapper.find(".condition-btn").on("click", function (e) {
      e.preventDefault();
      e.stopPropagation();

      const condition = $(this).data("condition");

      // Apply immediately
      window.surgishop.pendingCondition = condition;

      self.show_alert(
        `Condition "${condition}" will be applied to next scan`,
        "green",
        3
      );
      self.play_success_sound();
      dialog.hide();
    });
  }

  /**
   * Delete the last row from items table
   */
  delete_last_row() {
    const items = this.frm.doc[this.items_table_name] || [];
    if (items.length === 0) {
      this.show_alert("No items to delete", "orange");
      this.play_fail_sound();
      return;
    }

    const lastRow = items[items.length - 1];
    const itemCode = lastRow.item_code || "empty row";

    frappe.model.clear_doc(lastRow.doctype, lastRow.name);
    this.frm.refresh_field(this.items_table_name);

    this.show_alert(`Deleted row: ${itemCode}`, "red", 3);
    this.play_success_sound();
  }

  process_scan() {
    return new Promise((resolve, reject) => {
      try {
        const input = this.scan_barcode_field.value;
        this.scan_barcode_field.set_value("");
        if (!input) {
          return resolve();
        }

        // Check for trigger barcodes first
        if (this.check_trigger_barcode(input)) {
          return resolve();
        }

        // Try to parse as GS1 first
        const gs1_data = this.parse_gs1_string(input);

        if (gs1_data) {
          this.show_alert(
            `Scanned GS1 AIs:\nGTIN: ${gs1_data.gtin}\nExpiry: ${gs1_data.expiry}\nLot: ${gs1_data.lot}`,
            "blue",
            5
          );
          this.gs1_api_call(gs1_data, (r) =>
            this.handle_api_response(r, resolve, reject)
          );
        } else {
          this.scan_api_call(input, (r) =>
            this.handle_api_response(r, resolve, reject)
          );
        }
      } catch (e) {
        reject(e);
      }
    });
  }

  handle_api_response(r, resolve, reject) {
    try {
      const data = r && r.message;
      if (!data || Object.keys(data).length === 0 || data.error) {
        const error_msg =
          data && data.error
            ? data.error
            : "Cannot find Item with this Barcode";
        this.show_alert(
          `Error: ${error_msg}. Check console for details.`,
          "red"
        );
        this.clean_up();
        this.play_fail_sound();
        reject(new Error(error_msg));
        return;
      }

      // Handle warehouse-only responses
      if (data.warehouse && !data.item_code) {
        this.handle_warehouse_scan(data.warehouse);
        this.clean_up();
        this.play_success_sound();
        resolve();
        return;
      }

      // Handle item responses (with item_code)
      if (!data.item_code) {
        this.show_alert("No item found for this barcode", "red");
        this.clean_up();
        this.play_fail_sound();
        reject(new Error("No item found"));
        return;
      }

      this.update_table(data)
        .then((row) => {
          this.play_success_sound();
          resolve(row);
        })
        .catch((err) => {
          this.play_fail_sound();
          reject(err);
        });
    } catch (e) {
      reject(e);
    }
  }

  handle_warehouse_scan(warehouse_name) {
    if (frappe.meta.has_field(this.frm.doctype, "set_warehouse")) {
      frappe.model.set_value(
        this.frm.doctype,
        this.frm.doc.name,
        "set_warehouse",
        warehouse_name
      );
    }

    if (this.has_last_scanned_warehouse) {
      frappe.model.set_value(
        this.frm.doctype,
        this.frm.doc.name,
        "last_scanned_warehouse",
        warehouse_name
      );
    }

    this.show_alert(`Warehouse set to: ${warehouse_name}`, "green", 3);
    this.frm.refresh_fields();

    const warehouse_field = this.get_warehouse_field();
    if (
      warehouse_field &&
      frappe.meta.has_field(this.frm.doctype, this.items_table_name)
    ) {
      const items = this.frm.doc[this.items_table_name] || [];
      items.forEach((row) => {
        if (row[warehouse_field]) {
          frappe.model.set_value(row.doctype, row.name, warehouse_field, "");
        }
      });
    }
  }

  gs1_api_call(gs1_data, callback) {
    frappe
      .call({
        method: this.gs1_parser_api,
        args: {
          gtin: gs1_data.gtin,
          lot: gs1_data.lot,
          expiry: gs1_data.expiry,
        },
      })
      .then((r) => {
        if (r && r.message && r.message.found_item) {
          r.message.item_code = r.message.found_item;
          r.message.batch_no = r.message.batch;
          r.message.batch_expiry_date = r.message.batch_expiry_date;
        }
        callback(r);
      })
      .catch(() => {
        callback({
          message: {
            error:
              "GS1 API call failed. Please check connection or server logs.",
          },
        });
      });
  }

  scan_api_call(input, callback) {
    frappe
      .call({
        method: this.scan_api,
        args: {
          search_value: input,
          ctx: {
            set_warehouse: this.frm.doc.set_warehouse,
            company: this.frm.doc.company,
          },
        },
      })
      .then((r) => {
        callback(r);
      })
      .catch(() => {
        callback({
          message: {
            error:
              "Barcode API call failed. Please check connection or server logs.",
          },
        });
      });
  }

  update_table(data) {
    return new Promise((resolve, reject) => {
      let cur_grid = this.frm.fields_dict[this.items_table_name].grid;
      frappe.flags.trigger_from_barcode_scanner = true;

      const {
        item_code,
        barcode,
        batch_no,
        batch_expiry_date,
        serial_no,
        uom,
        default_warehouse,
      } = data;

      // Check for pending condition FIRST
      // Condition scans should ALWAYS create a new row
      const pendingCondition = window.surgishop.pendingCondition;
      if (pendingCondition) {
        window.surgishop.pendingCondition = null;
      }

      // Check if we're forcing a new row (or if condition is pending)
      let forceNewRow = window.surgishop.forceNewRow || !!pendingCondition;
      if (window.surgishop.forceNewRow) {
        window.surgishop.forceNewRow = false;
      }

      // Check if we should prompt for quantity
      const shouldPromptQty =
        window.surgishop.forcePromptQty || this.prompt_qty;
      if (window.surgishop.forcePromptQty) {
        window.surgishop.forcePromptQty = false;
      }

      let row = forceNewRow
        ? null
        : this.get_row_to_modify_on_scan(
            item_code,
            batch_no,
            uom,
            barcode,
            default_warehouse,
            pendingCondition
          );
      const is_new_row = row && row.item_code ? false : true;

      if (!row) {
        if (this.dont_allow_new_row && !forceNewRow) {
          this.show_alert(
            `Maximum quantity scanned for item ${item_code}.`,
            "red"
          );
          this.clean_up();
          reject();
          return;
        }

        row = frappe.model.add_child(
          this.frm.doc,
          cur_grid.doctype,
          this.items_table_name
        );
        this.frm.script_manager.trigger(
          `${this.items_table_name}_add`,
          row.doctype,
          row.name
        );
        cur_grid.refresh();
        this.frm.has_items = false;
      }

      if (this.is_duplicate_serial_no(row, serial_no)) {
        this.clean_up();
        reject();
        return;
      }

      // Longer delay for new rows to ensure DOM is fully rendered
      const initialDelay = is_new_row ? 500 : 100;

      frappe.run_serially([
        () => this.set_selector_trigger_flag(data),
        () => new Promise((resolve) => setTimeout(resolve, initialDelay)),
        () =>
          this.set_item(
            row,
            item_code,
            barcode,
            batch_no,
            serial_no,
            shouldPromptQty
          ).then((qty) => {
            this.show_scan_message(row.idx, !is_new_row, qty);
          }),
        () => this.set_barcode_uom(row, uom),
        () => this.set_serial_no(row, serial_no),
        () => this.set_batch_no(row, batch_no),
        () => this.set_batch_expiry_date(row, batch_expiry_date),
        () => this.set_barcode(row, barcode),
        () => this.set_warehouse(row),
        () => this.set_condition(row, pendingCondition),
        () => this.clean_up(),
        () => this.revert_selector_flag(),
        () => resolve(row),
      ]);
    });
  }

  set_selector_trigger_flag(data) {
    const settings = window.surgishop.settings;

    // If globally disabled, always hide the dialog
    if (settings.disableSerialBatchSelector) {
      frappe.flags.hide_serial_batch_dialog = true;
      return;
    }

    const { batch_no, serial_no, has_batch_no, has_serial_no } = data;
    const require_selecting_batch = has_batch_no && !batch_no;
    const require_selecting_serial = has_serial_no && !serial_no;

    if (!(require_selecting_batch || require_selecting_serial)) {
      frappe.flags.hide_serial_batch_dialog = true;
    }
  }

  revert_selector_flag() {
    frappe.flags.hide_serial_batch_dialog = false;
    frappe.flags.trigger_from_barcode_scanner = false;
  }

  set_item(
    row,
    item_code,
    barcode,
    batch_no,
    serial_no,
    shouldPromptQty = false
  ) {
    return new Promise((resolve) => {
      const increment = async (value) => {
        const qty = value !== undefined ? value : this.default_qty;
        const item_data = {
          item_code: item_code,
          use_serial_batch_fields: 1.0,
        };
        frappe.flags.trigger_from_barcode_scanner = true;
        item_data[this.qty_field] =
          Number(row[this.qty_field] || 0) + Number(qty);
        try {
          await frappe.model.set_value(row.doctype, row.name, item_data);
        } catch (e) {
          // ERPNext internal handlers may throw errors when refreshing fields
          // before DOM is ready - this is harmless
        }
        return qty;
      };

      if (shouldPromptQty) {
        frappe.prompt(
          {
            fieldtype: "Float",
            label: `Enter quantity for ${item_code}`,
            fieldname: "value",
            default: this.default_qty,
            reqd: 1,
          },
          ({ value }) => {
            increment(value).then((qty) => resolve(qty));
          },
          "Enter Quantity",
          "Add"
        );
      } else if (this.frm.has_items) {
        this.prepare_item_for_scan(
          row,
          item_code,
          barcode,
          batch_no,
          serial_no
        );
        resolve(this.default_qty);
      } else {
        increment().then((qty) => resolve(qty));
      }
    });
  }

  prepare_item_for_scan(row, item_code, barcode, batch_no, serial_no) {
    return new Promise((resolve) => {
      const increment = async (value) => {
        const qty = value !== undefined ? value : this.default_qty;
        const item_data = {
          item_code: item_code,
          use_serial_batch_fields: 1.0,
        };
        frappe.flags.trigger_from_barcode_scanner = true;
        item_data[this.qty_field] =
          Number(row[this.qty_field] || 0) + Number(qty);
        try {
          await frappe.model.set_value(row.doctype, row.name, item_data);
        } catch (e) {
          // Safe to ignore
        }
        return qty;
      };

      increment().then((qty) => resolve(qty));
    });
  }

  async set_serial_no(row, serial_no) {
    if (serial_no && frappe.meta.has_field(row.doctype, this.serial_no_field)) {
      try {
        const existing_serial_nos = row[this.serial_no_field];
        let new_serial_nos = "";

        if (!!existing_serial_nos) {
          new_serial_nos = existing_serial_nos + "\n" + serial_no;
        } else {
          new_serial_nos = serial_no;
        }
        await frappe.model.set_value(
          row.doctype,
          row.name,
          this.serial_no_field,
          new_serial_nos
        );
      } catch (e) {
        // ERPNext internal refresh errors - safe to ignore
      }
    }
  }

  async set_barcode_uom(row, uom) {
    if (uom && frappe.meta.has_field(row.doctype, this.uom_field)) {
      try {
        await frappe.model.set_value(
          row.doctype,
          row.name,
          this.uom_field,
          uom
        );
      } catch (e) {
        // ERPNext internal refresh errors - safe to ignore
      }
    }
  }

  async set_batch_no(row, batch_no) {
    if (batch_no && frappe.meta.has_field(row.doctype, this.batch_no_field)) {
      try {
        await frappe.model.set_value(
          row.doctype,
          row.name,
          this.batch_no_field,
          batch_no
        );
      } catch (e) {
        // ERPNext internal refresh errors - safe to ignore
      }
    }
  }

  async set_batch_expiry_date(row, batch_expiry_date) {
    if (
      batch_expiry_date &&
      frappe.meta.has_field(row.doctype, this.batch_expiry_date_field)
    ) {
      try {
        await frappe.model.set_value(
          row.doctype,
          row.name,
          this.batch_expiry_date_field,
          batch_expiry_date
        );
      } catch (e) {
        // ERPNext internal refresh errors - safe to ignore
      }
    }
  }

  async set_barcode(row, barcode) {
    if (barcode && frappe.meta.has_field(row.doctype, this.barcode_field)) {
      try {
        await frappe.model.set_value(
          row.doctype,
          row.name,
          this.barcode_field,
          barcode
        );
      } catch (e) {
        // ERPNext internal refresh errors - safe to ignore
      }
    }
  }

  async set_warehouse(row) {
    if (!this.has_last_scanned_warehouse) return;

    const last_scanned_warehouse = this.frm.doc.last_scanned_warehouse;
    if (!last_scanned_warehouse) return;

    const warehouse_field = this.get_warehouse_field();
    if (
      !warehouse_field ||
      !frappe.meta.has_field(row.doctype, warehouse_field)
    )
      return;

    try {
      await frappe.model.set_value(
        row.doctype,
        row.name,
        warehouse_field,
        last_scanned_warehouse
      );
    } catch (e) {
      // ERPNext internal refresh errors - safe to ignore
    }
  }

  async set_condition(row, condition) {
    if (!condition) return;

    if (frappe.meta.has_field(row.doctype, this.condition_field)) {
      try {
        await frappe.model.set_value(
          row.doctype,
          row.name,
          this.condition_field,
          condition
        );
      } catch (e) {
        // ERPNext internal refresh errors - safe to ignore
      }
    }
  }

  get_warehouse_field() {
    if (typeof this.warehouse_field === "function") {
      return this.warehouse_field(this.frm.doc);
    }
    return this.warehouse_field;
  }

  show_scan_message(idx, is_existing_row = false, qty = 1) {
    if (is_existing_row) {
      this.show_alert(`Row #${idx}: Qty increased by ${qty}`, "green");
    } else {
      const current_warehouse = this.frm.doc.last_scanned_warehouse;
      const warehouse_msg = current_warehouse ? ` in ${current_warehouse}` : "";
      this.show_alert(`Row #${idx}: Item added${warehouse_msg}`, "green");
    }
  }

  is_duplicate_serial_no(row, serial_no) {
    if (
      row &&
      row[this.serial_no_field] &&
      row[this.serial_no_field].includes(serial_no)
    ) {
      this.show_alert(`Serial No ${serial_no} is already added`, "orange");
      return true;
    }
    return false;
  }

  get_row_to_modify_on_scan(
    item_code,
    batch_no,
    uom,
    barcode,
    default_warehouse,
    pendingCondition = null
  ) {
    let cur_grid = this.frm.fields_dict[this.items_table_name].grid;

    let is_batch_no_scan =
      batch_no && frappe.meta.has_field(cur_grid.doctype, this.batch_no_field);
    let check_max_qty =
      this.max_qty_field &&
      frappe.meta.has_field(cur_grid.doctype, this.max_qty_field);

    const warehouse_field = this.get_warehouse_field();
    const has_warehouse_field =
      warehouse_field &&
      frappe.meta.has_field(cur_grid.doctype, warehouse_field);

    const warehouse = has_warehouse_field
      ? this.frm.doc.last_scanned_warehouse ||
        this.frm.doc.set_warehouse ||
        default_warehouse
      : null;

    // Check if condition field exists on the child doctype
    const has_condition_field = frappe.meta.has_field(
      cur_grid.doctype,
      this.condition_field
    );

    const matching_row = (row) => {
      const item_match = row.item_code == item_code;

      // For batch matching
      const row_batch = row[this.batch_no_field] || "";
      const scan_batch = batch_no || "";
      let batch_match = true;
      if (is_batch_no_scan) {
        batch_match = !row_batch || row_batch === scan_batch;
      }

      const uom_match = !uom || row[this.uom_field] == uom;

      const max_qty = flt(row[this.max_qty_field]);
      const qty_in_limit =
        max_qty > 0 ? flt(row[this.qty_field]) < max_qty : true;

      let warehouse_match = true;
      if (has_warehouse_field && warehouse_field) {
        const current_warehouse = warehouse || null;
        const existing_warehouse = row[warehouse_field] || null;

        if (current_warehouse && existing_warehouse) {
          warehouse_match = current_warehouse === existing_warehouse;
        } else {
          warehouse_match = true;
        }
      }

      // Condition matching:
      // - Normal scan (no condition) should NOT match rows that have a condition
      // - Condition scan should only match rows with the SAME condition
      let condition_match = true;
      if (has_condition_field) {
        const row_condition = row[this.condition_field] || "";
        const scan_condition = pendingCondition || "";

        if (scan_condition) {
          condition_match = row_condition === scan_condition;
        } else {
          condition_match = !row_condition;
        }
      }

      const matches =
        item_match &&
        uom_match &&
        warehouse_match &&
        batch_match &&
        condition_match &&
        (!check_max_qty || qty_in_limit);

      return matches;
    };

    const items_table = this.frm.doc[this.items_table_name] || [];
    return (
      items_table.find(matching_row) || items_table.find((d) => !d.item_code)
    );
  }

  play_success_sound() {
    if (this.enable_sounds && this.success_sound) {
      frappe.utils.play_sound(this.success_sound);
    }
  }

  play_fail_sound() {
    if (this.enable_sounds && this.fail_sound) {
      frappe.utils.play_sound(this.fail_sound);
    }
  }

  clean_up() {
    this.scan_barcode_field.set_value("");
    refresh_field(this.items_table_name);
  }

  show_alert(msg, indicator, duration = 3) {
    frappe.show_alert(
      {
        message: msg,
        indicator: indicator,
      },
      duration
    );
  }
};

/**
 * Load all scanner settings from SurgiShop Settings
 */
function loadSurgiShopScannerSettings() {
  frappe.call({
    method: "frappe.client.get_value",
    args: {
      doctype: "SurgiShop Settings",
      fieldname: [
        "enable_scan_sounds",
        "prompt_for_quantity",
        "default_scan_quantity",
        "auto_create_batches",
        "disable_serial_batch_selector",
        "new_line_trigger_barcode",
        "condition_trigger_barcode",
        "quantity_trigger_barcode",
        "delete_row_trigger_barcode",
        "warn_on_expiry_mismatch",
        "update_missing_expiry",
        "strict_gtin_validation",
      ],
    },
    async: true,
    callback: (r) => {
      if (r && r.message) {
        const s = r.message;
        window.surgishop.settings = {
          enableScanSounds: s.enable_scan_sounds !== 0,
          promptForQuantity: s.prompt_for_quantity === 1,
          defaultScanQuantity: s.default_scan_quantity || 1,
          autoCreateBatches: s.auto_create_batches !== 0,
          disableSerialBatchSelector: s.disable_serial_batch_selector !== 0,
          newLineTriggerBarcode: s.new_line_trigger_barcode || null,
          conditionTriggerBarcode: s.condition_trigger_barcode || null,
          quantityTriggerBarcode: s.quantity_trigger_barcode || null,
          deleteRowTriggerBarcode: s.delete_row_trigger_barcode || null,
          warnOnExpiryMismatch: s.warn_on_expiry_mismatch !== 0,
          updateMissingExpiry: s.update_missing_expiry !== 0,
          strictGtinValidation: s.strict_gtin_validation === 1,
        };

        // Apply global flag to disable serial/batch selector
        if (window.surgishop.settings.disableSerialBatchSelector) {
          frappe.flags.hide_serial_batch_dialog = true;
        }
      }
    },
  });
}

// Load settings on page load
$(document).ready(() => {
  loadSurgiShopScannerSettings();
});

/**
 * This is the main override logic.
 * We wrap this in a router 'change' event to ensure the Frappe framework is fully
 * loaded and ready before we try to attach our form-specific hooks.
 */
frappe.router.on("change", () => {
  const doctypes_to_override = [
    "Stock Entry",
    "Purchase Order",
    "Purchase Receipt",
    "Purchase Invoice",
    "Sales Invoice",
    "Delivery Note",
    "Stock Reconciliation",
  ];

  if (
    frappe.get_route() &&
    frappe.get_route()[0] === "Form" &&
    doctypes_to_override.includes(frappe.get_route()[1])
  ) {
    const frm = cur_frm;
    if (frm && !frm.custom_scanner_attached) {
      frappe.ui.form.on(frappe.get_route()[1], {
        scan_barcode: function (frm) {
          const opts = frm.events.get_barcode_scanner_options
            ? frm.events.get_barcode_scanner_options(frm)
            : {};
          opts.frm = frm;

          const scanner = new surgishop.CustomBarcodeScanner(opts);
          scanner.process_scan().catch(() => {
            frappe.show_alert({
              message: "Barcode scan failed. Please try again.",
              indicator: "red",
            });
          });
        },
      });
      frm.custom_scanner_attached = true;
    }
  }
});

/**
 * Auto-fetch expiry date when batch_no is manually changed in child tables
 * This handles cases where users select a batch manually (not via scanner)
 */
function setupBatchExpiryAutoFetch() {
  const childDoctypes = [
    "Purchase Receipt Item",
    "Purchase Invoice Item",
    "Stock Entry Detail",
    "Delivery Note Item",
    "Sales Invoice Item",
  ];

  childDoctypes.forEach((childDoctype) => {
    frappe.ui.form.on(childDoctype, {
      batch_no: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const batchNo = row.batch_no;

        if (batchNo) {
          frappe.db.get_value("Batch", batchNo, "expiry_date", (r) => {
            if (r && r.expiry_date) {
              frappe.model.set_value(
                cdt,
                cdn,
                "custom_expiration_date",
                r.expiry_date
              );
            } else {
              frappe.model.set_value(cdt, cdn, "custom_expiration_date", null);
            }
          });
        } else {
          frappe.model.set_value(cdt, cdn, "custom_expiration_date", null);
        }
      },
    });
  });
}

// Initialize batch expiry auto-fetch on page ready
$(document).ready(() => {
  setupBatchExpiryAutoFetch();
});
