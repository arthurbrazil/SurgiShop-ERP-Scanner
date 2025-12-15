/**
 * SurgiShop ERP Scanner - Custom Barcode Scanner Override
 * Overrides ERPNext's default barcode scanning with custom functionality
 */

console.log(
  `%c🏥 SurgiShop ERP Scanner: Global JS file loaded.`,
  "color: #1E88E5; font-weight: bold;"
)

// Namespace for our custom code to avoid polluting the global scope
if (typeof window.surgishop === "undefined") {
  window.surgishop = {}
}

// Scanner state flags
window.surgishop.forceNewRow = false
window.surgishop.forcePromptQty = false
window.surgishop.pendingCondition = null

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
}

/**
 * Our custom scanner class.
 * All the logic for parsing and handling scans is contained here.
 */
surgishop.CustomBarcodeScanner = class CustomBarcodeScanner {
  constructor(opts) {
    console.log("🏥 SurgiShop ERP Scanner: Custom BarcodeScanner created")
    this.frm = opts.frm
    this.scan_field_name = opts.scan_field_name || "scan_barcode"
    this.scan_barcode_field = this.frm.fields_dict[this.scan_field_name]
    this.barcode_field = opts.barcode_field || "barcode"
    this.serial_no_field = opts.serial_no_field || "serial_no"
    this.batch_no_field = opts.batch_no_field || "batch_no"
    this.batch_expiry_date_field =
      opts.batch_expiry_date_field || "custom_expiration_date"
    this.uom_field = opts.uom_field || "uom"
    this.qty_field = opts.qty_field || "qty"
    this.warehouse_field = opts.warehouse_field || "warehouse"
    this.condition_field = opts.condition_field || "custom_condition"
    this.max_qty_field = opts.max_qty_field
    this.dont_allow_new_row = opts.dont_allow_new_row
    this.items_table_name = opts.items_table_name || "items"

    // Use settings for sounds
    const settings = window.surgishop.settings
    this.enable_sounds = settings.enableScanSounds
    this.success_sound = this.enable_sounds ? "submit" : null
    this.fail_sound = this.enable_sounds ? "error" : null

    // Use settings for quantity behavior
    this.prompt_qty = opts.prompt_qty || settings.promptForQuantity
    this.default_qty = settings.defaultScanQuantity || 1

    this.scan_api =
      opts.scan_api ||
      "surgishop_erp_scanner.surgishop_erp_scanner.api.barcode.scan_barcode"
    this.gs1_parser_api =
      "surgishop_erp_scanner.surgishop_erp_scanner.api.gs1_parser.parse_gs1_and_get_batch"
    this.has_last_scanned_warehouse = frappe.meta.has_field(
      this.frm.doctype,
      "last_scanned_warehouse"
    )
  }

  /**
   * Parses a GS1 string using the shared GS1Parser utility.
   * @param {string} gs1_string The raw scanned string
   * @returns {object|null} Parsed data {gtin, lot, expiry} or null if not matching
   */
  parse_gs1_string(gs1_string) {
    // Use the shared GS1Parser utility
    if (window.surgishop && window.surgishop.GS1Parser) {
      return window.surgishop.GS1Parser.parse(gs1_string)
    } else {
      console.error(
        "🏥 GS1Parser not loaded! Make sure gs1-utils.js is included."
      )
      return null
    }
  }

  /**
   * Check if this is a special trigger barcode
   * @param {string} input The scanned barcode
   * @returns {boolean} True if this is a trigger barcode that was handled
   */
  check_trigger_barcode(input) {
    const settings = window.surgishop.settings

    // New Line Trigger
    if (settings.newLineTriggerBarcode && input === settings.newLineTriggerBarcode) {
      console.log(
        `%c🏥 NEW LINE TRIGGER scanned! Next item will be added on a new row.`,
        "color: #FF9800; font-weight: bold;"
      )
      window.surgishop.forceNewRow = true
      this.show_alert("New Line Mode: Next scan will create a new row", "orange", 3)
      this.play_success_sound()
      return true
    }

    // Condition Trigger
    if (settings.conditionTriggerBarcode && input === settings.conditionTriggerBarcode) {
      console.log(
        `%c🏥 CONDITION TRIGGER scanned! Enter condition for next item.`,
        "color: #9C27B0; font-weight: bold;"
      )
      this.prompt_for_condition()
      return true
    }

    // Quantity Trigger
    if (settings.quantityTriggerBarcode && input === settings.quantityTriggerBarcode) {
      console.log(
        `%c🏥 QUANTITY TRIGGER scanned! Next scan will prompt for quantity.`,
        "color: #2196F3; font-weight: bold;"
      )
      window.surgishop.forcePromptQty = true
      this.show_alert("Quantity Mode: Next scan will prompt for quantity", "blue", 3)
      this.play_success_sound()
      return true
    }

    // Delete Row Trigger
    if (settings.deleteRowTriggerBarcode && input === settings.deleteRowTriggerBarcode) {
      console.log(
        `%c🏥 DELETE ROW TRIGGER scanned! Removing last row.`,
        "color: #F44336; font-weight: bold;"
      )
      this.delete_last_row()
      return true
    }

    return false
  }

  /**
   * Prompt for condition selection
   */
  prompt_for_condition() {
    // Get condition options from the field
    const conditionField = frappe.meta.get_docfield(
      this.frm.doctype + " Item",
      this.condition_field
    ) || frappe.meta.get_docfield(
      "Purchase Receipt Item",
      this.condition_field
    )

    let options = []
    if (conditionField && conditionField.options) {
      options = conditionField.options.split("\n").filter(o => o.trim())
    }

    if (options.length === 0) {
      this.show_alert("No condition options configured", "orange")
      return
    }

    frappe.prompt(
      {
        fieldtype: "Select",
        label: "Select Condition for Next Scan",
        fieldname: "condition",
        options: options,
        reqd: 1,
      },
      (values) => {
        window.surgishop.pendingCondition = values.condition
        this.show_alert(`Condition "${values.condition}" will be applied to next scan`, "green", 3)
        this.play_success_sound()
      },
      "Set Condition",
      "Apply"
    )
  }

  /**
   * Delete the last row from items table
   */
  delete_last_row() {
    const items = this.frm.doc[this.items_table_name] || []
    if (items.length === 0) {
      this.show_alert("No items to delete", "orange")
      this.play_fail_sound()
      return
    }

    const lastRow = items[items.length - 1]
    const itemCode = lastRow.item_code || "empty row"

    frappe.model.clear_doc(lastRow.doctype, lastRow.name)
    this.frm.refresh_field(this.items_table_name)

    this.show_alert(`Deleted row: ${itemCode}`, "red", 3)
    this.play_success_sound()
  }

  process_scan() {
    console.log(
      "🏥 SurgiShop ERP Scanner: OVERRIDE SUCCESS! Custom process_scan method is running."
    )
    return new Promise((resolve, reject) => {
      try {
        const input = this.scan_barcode_field.value
        this.scan_barcode_field.set_value("")
        if (!input) {
          return resolve()
        }

        console.log("🏥 SurgiShop ERP Scanner: Processing barcode scan:", input)

        // Check for trigger barcodes first
        if (this.check_trigger_barcode(input)) {
          return resolve()
        }

        // Try to parse as GS1 first
        const gs1_data = this.parse_gs1_string(input)

        if (gs1_data) {
          console.log(
            "🏥 SurgiShop ERP Scanner: Detected GS1 barcode. Parsed:",
            gs1_data
          )
          console.log(
            `%c🏥 Scanned GS1 AIs: AI01 (GTIN)=${gs1_data.gtin}, AI17 (Expiry)=${gs1_data.expiry}, AI10 (Lot)=${gs1_data.lot}`,
            "color: #2196F3; font-weight: bold;"
          )
          this.show_alert(
            `Scanned GS1 AIs:\nGTIN: ${gs1_data.gtin}\nExpiry: ${gs1_data.expiry}\nLot: ${gs1_data.lot}`,
            "blue",
            5
          )
          this.gs1_api_call(gs1_data, (r) =>
            this.handle_api_response(r, resolve, reject)
          )
        } else {
          console.log(
            "🏥 SurgiShop ERP Scanner: Not a GS1 barcode, using standard scan."
          )
          this.scan_api_call(input, (r) =>
            this.handle_api_response(r, resolve, reject)
          )
        }
      } catch (e) {
        console.error("🏥 SurgiShop ERP Scanner: FATAL ERROR in process_scan:", e)
        reject(e)
      }
    })
  }

  handle_api_response(r, resolve, reject) {
    try {
      const data = r && r.message
      if (!data || Object.keys(data).length === 0 || data.error) {
        const error_msg =
          data && data.error
            ? data.error
            : "Cannot find Item with this Barcode"
        console.warn(
          `%c🏥 Scan Error: ${error_msg}. Response details:`,
          "color: #FF5722;",
          r
        )
        this.show_alert(
          `Error: ${error_msg}. Check console for details.`,
          "red"
        )
        this.clean_up()
        this.play_fail_sound()
        reject(new Error(error_msg))
        return
      }

      console.log("🏥 SurgiShop ERP Scanner: Barcode scan result:", data)

      // Handle warehouse-only responses
      if (data.warehouse && !data.item_code) {
        console.log("🏥 SurgiShop ERP Scanner: Warehouse scanned:", data.warehouse)
        this.handle_warehouse_scan(data.warehouse)
        this.clean_up()
        this.play_success_sound()
        resolve()
        return
      }

      // Handle item responses (with item_code)
      if (!data.item_code) {
        console.warn(
          "🏥 SurgiShop ERP Scanner: No item_code in response, treating as error"
        )
        this.show_alert("No item found for this barcode", "red")
        this.clean_up()
        this.play_fail_sound()
        reject(new Error("No item found"))
        return
      }

      this.update_table(data)
        .then((row) => {
          this.play_success_sound()
          resolve(row)
        })
        .catch((err) => {
          this.play_fail_sound()
          reject(err)
        })
    } catch (e) {
      console.error(
        "🏥 SurgiShop ERP Scanner: FATAL ERROR in handle_api_response:",
        e
      )
      reject(e)
    }
  }

  handle_warehouse_scan(warehouse_name) {
    console.log(
      `🏥 SurgiShop ERP Scanner: Handling warehouse scan: ${warehouse_name}`
    )

    if (frappe.meta.has_field(this.frm.doctype, "set_warehouse")) {
      frappe.model.set_value(
        this.frm.doctype,
        this.frm.doc.name,
        "set_warehouse",
        warehouse_name
      )
      console.log(
        `🏥 SurgiShop ERP Scanner: Set document warehouse to: ${warehouse_name}`
      )
    }

    if (this.has_last_scanned_warehouse) {
      frappe.model.set_value(
        this.frm.doctype,
        this.frm.doc.name,
        "last_scanned_warehouse",
        warehouse_name
      )
      console.log(
        `🏥 SurgiShop ERP Scanner: Stored last scanned warehouse: ${warehouse_name}`
      )
    }

    this.show_alert(`Warehouse set to: ${warehouse_name}`, "green", 3)
    this.frm.refresh_fields()

    const warehouse_field = this.get_warehouse_field()
    if (warehouse_field && frappe.meta.has_field(this.frm.doctype, this.items_table_name)) {
      const items = this.frm.doc[this.items_table_name] || []
      items.forEach((row, index) => {
        if (row[warehouse_field]) {
          console.log(`🏥 SurgiShop ERP Scanner: Clearing warehouse from existing row ${index + 1} to force new row creation`)
          frappe.model.set_value(row.doctype, row.name, warehouse_field, "")
        }
      })
    }
  }

  gs1_api_call(gs1_data, callback) {
    console.log("🏥 SurgiShop ERP Scanner: Calling GS1 parser API:", gs1_data)
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
        console.log("🏥 SurgiShop ERP Scanner: GS1 API response:", r)
        if (r && r.message && r.message.found_item) {
          r.message.item_code = r.message.found_item
          r.message.batch_no = r.message.batch
          r.message.batch_expiry_date = r.message.batch_expiry_date
        }
        callback(r)
      })
      .catch((error) => {
        console.error("🏥 SurgiShop ERP Scanner: GS1 API call failed:", error)
        callback({
          message: {
            error:
              "GS1 API call failed. Please check connection or server logs.",
          },
        })
      })
  }

  scan_api_call(input, callback) {
    console.log("🏥 SurgiShop ERP Scanner: Calling custom barcode API:", input)

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
        console.log("🏥 SurgiShop ERP Scanner: API response:", r)
        callback(r)
      })
      .catch((error) => {
        console.error("🏥 SurgiShop ERP Scanner: Standard API call failed:", error)
        callback({
          message: {
            error:
              "Barcode API call failed. Please check connection or server logs.",
          },
        })
      })
  }

  update_table(data) {
    return new Promise((resolve, reject) => {
      let cur_grid = this.frm.fields_dict[this.items_table_name].grid
      frappe.flags.trigger_from_barcode_scanner = true

      const {
        item_code,
        barcode,
        batch_no,
        batch_expiry_date,
        serial_no,
        uom,
        default_warehouse,
      } = data

      // Check if we're forcing a new row
      const forceNewRow = window.surgishop.forceNewRow
      if (forceNewRow) {
        console.log(
          `%c🏥 FORCE NEW ROW mode active - will create new row regardless of matching`,
          "color: #FF9800; font-weight: bold;"
        )
        window.surgishop.forceNewRow = false
      }

      // Check if we should prompt for quantity
      const shouldPromptQty = window.surgishop.forcePromptQty || this.prompt_qty
      if (window.surgishop.forcePromptQty) {
        window.surgishop.forcePromptQty = false
      }

      // Check for pending condition
      const pendingCondition = window.surgishop.pendingCondition
      if (pendingCondition) {
        window.surgishop.pendingCondition = null
      }

      let row = forceNewRow
        ? null
        : this.get_row_to_modify_on_scan(
            item_code,
            batch_no,
            uom,
            barcode,
            default_warehouse
          )
      const is_new_row = row && row.item_code ? false : true

      if (is_new_row && item_code) {
        const current_warehouse =
          this.frm.doc.last_scanned_warehouse ||
          this.frm.doc.set_warehouse ||
          default_warehouse
        console.log(
          `🏥 SurgiShop ERP Scanner: Creating new row for item ${item_code} in warehouse ${current_warehouse}`
        )
        if (forceNewRow) {
          console.log(`🏥 Debug - Reason: FORCE NEW ROW mode was active`)
        } else {
          console.log(`🏥 Debug - Reason: No matching row found with same warehouse`)
        }
      } else if (!is_new_row && item_code) {
        const current_warehouse =
          this.frm.doc.last_scanned_warehouse ||
          this.frm.doc.set_warehouse ||
          default_warehouse
        console.log(
          `🏥 SurgiShop ERP Scanner: Incrementing existing row for item ${item_code} in warehouse ${current_warehouse}`
        )
      }

      if (!row) {
        if (this.dont_allow_new_row && !forceNewRow) {
          this.show_alert(
            `Maximum quantity scanned for item ${item_code}.`,
            "red"
          )
          this.clean_up()
          reject()
          return
        }

        row = frappe.model.add_child(
          this.frm.doc,
          cur_grid.doctype,
          this.items_table_name
        )
        this.frm.script_manager.trigger(
          `${this.items_table_name}_add`,
          row.doctype,
          row.name
        )
        this.frm.has_items = false
      }

      if (this.is_duplicate_serial_no(row, serial_no)) {
        this.clean_up()
        reject()
        return
      }

      frappe.run_serially([
        () => this.set_selector_trigger_flag(data),
        () =>
          this.set_item(row, item_code, barcode, batch_no, serial_no, shouldPromptQty).then(
            (qty) => {
              this.show_scan_message(row.idx, !is_new_row, qty)
            }
          ),
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
      ])
    })
  }

  set_selector_trigger_flag(data) {
    const settings = window.surgishop.settings

    // If globally disabled, always hide the dialog
    if (settings.disableSerialBatchSelector) {
      frappe.flags.hide_serial_batch_dialog = true
      return
    }

    const { batch_no, serial_no, has_batch_no, has_serial_no } = data
    const require_selecting_batch = has_batch_no && !batch_no
    const require_selecting_serial = has_serial_no && !serial_no

    if (!(require_selecting_batch || require_selecting_serial)) {
      frappe.flags.hide_serial_batch_dialog = true
    }
  }

  revert_selector_flag() {
    frappe.flags.hide_serial_batch_dialog = false
    frappe.flags.trigger_from_barcode_scanner = false
  }

  set_item(row, item_code, barcode, batch_no, serial_no, shouldPromptQty = false) {
    return new Promise((resolve) => {
      const increment = async (value) => {
        const qty = value !== undefined ? value : this.default_qty
        const item_data = {
          item_code: item_code,
          use_serial_batch_fields: 1.0,
        }
        frappe.flags.trigger_from_barcode_scanner = true
        item_data[this.qty_field] =
          Number(row[this.qty_field] || 0) + Number(qty)
        await frappe.model.set_value(row.doctype, row.name, item_data)
        return qty
      }

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
            increment(value).then((qty) => resolve(qty))
          },
          "Enter Quantity",
          "Add"
        )
      } else if (this.frm.has_items) {
        this.prepare_item_for_scan(row, item_code, barcode, batch_no, serial_no)
        resolve(this.default_qty)
      } else {
        increment().then((qty) => resolve(qty))
      }
    })
  }

  prepare_item_for_scan(row, item_code, barcode, batch_no, serial_no) {
    return new Promise((resolve) => {
      const increment = async (value) => {
        const qty = value !== undefined ? value : this.default_qty
        const item_data = {
          item_code: item_code,
          use_serial_batch_fields: 1.0,
        }
        item_data[this.qty_field] =
          Number(row[this.qty_field] || 0) + Number(qty)
        await frappe.model.set_value(row.doctype, row.name, item_data)
        return qty
      }

      increment().then((qty) => resolve(qty))
    })
  }

  async set_serial_no(row, serial_no) {
    if (serial_no && frappe.meta.has_field(row.doctype, this.serial_no_field)) {
      const existing_serial_nos = row[this.serial_no_field]
      let new_serial_nos = ""

      if (!!existing_serial_nos) {
        new_serial_nos = existing_serial_nos + "\n" + serial_no
      } else {
        new_serial_nos = serial_no
      }
      await frappe.model.set_value(
        row.doctype,
        row.name,
        this.serial_no_field,
        new_serial_nos
      )
    }
  }

  async set_barcode_uom(row, uom) {
    if (uom && frappe.meta.has_field(row.doctype, this.uom_field)) {
      await frappe.model.set_value(row.doctype, row.name, this.uom_field, uom)
    }
  }

  async set_batch_no(row, batch_no) {
    if (batch_no && frappe.meta.has_field(row.doctype, this.batch_no_field)) {
      await frappe.model.set_value(
        row.doctype,
        row.name,
        this.batch_no_field,
        batch_no
      )
    }
  }

  async set_batch_expiry_date(row, batch_expiry_date) {
    if (
      batch_expiry_date &&
      frappe.meta.has_field(row.doctype, this.batch_expiry_date_field)
    ) {
      console.log(
        `🏥 SurgiShop ERP Scanner: Setting batch expiry date: ${batch_expiry_date}`
      )
      await frappe.model.set_value(
        row.doctype,
        row.name,
        this.batch_expiry_date_field,
        batch_expiry_date
      )
    }
  }

  async set_barcode(row, barcode) {
    if (barcode && frappe.meta.has_field(row.doctype, this.barcode_field)) {
      await frappe.model.set_value(
        row.doctype,
        row.name,
        this.barcode_field,
        barcode
      )
    }
  }

  async set_warehouse(row) {
    if (!this.has_last_scanned_warehouse) return

    const last_scanned_warehouse = this.frm.doc.last_scanned_warehouse
    if (!last_scanned_warehouse) return

    const warehouse_field = this.get_warehouse_field()
    if (
      !warehouse_field ||
      !frappe.meta.has_field(row.doctype, warehouse_field)
    )
      return

    await frappe.model.set_value(
      row.doctype,
      row.name,
      warehouse_field,
      last_scanned_warehouse
    )
  }

  async set_condition(row, condition) {
    if (!condition) return

    if (frappe.meta.has_field(row.doctype, this.condition_field)) {
      console.log(
        `🏥 SurgiShop ERP Scanner: Setting condition: ${condition}`
      )
      await frappe.model.set_value(
        row.doctype,
        row.name,
        this.condition_field,
        condition
      )
    } else {
      console.warn(
        `🏥 SurgiShop ERP Scanner: Condition field ${this.condition_field} not found on ${row.doctype}`
      )
    }
  }

  get_warehouse_field() {
    if (typeof this.warehouse_field === "function") {
      return this.warehouse_field(this.frm.doc)
    }
    return this.warehouse_field
  }

  show_scan_message(idx, is_existing_row = false, qty = 1) {
    if (is_existing_row) {
      this.show_alert(`Row #${idx}: Qty increased by ${qty}`, "green")
    } else {
      const current_warehouse = this.frm.doc.last_scanned_warehouse
      const warehouse_msg = current_warehouse ? ` in ${current_warehouse}` : ""
      this.show_alert(`Row #${idx}: Item added${warehouse_msg}`, "green")
    }
  }

  is_duplicate_serial_no(row, serial_no) {
    if (
      row &&
      row[this.serial_no_field] &&
      row[this.serial_no_field].includes(serial_no)
    ) {
      this.show_alert(`Serial No ${serial_no} is already added`, "orange")
      return true
    }
    return false
  }

  get_row_to_modify_on_scan(
    item_code,
    batch_no,
    uom,
    barcode,
    default_warehouse
  ) {
    let cur_grid = this.frm.fields_dict[this.items_table_name].grid

    let is_batch_no_scan =
      batch_no && frappe.meta.has_field(cur_grid.doctype, this.batch_no_field)
    let check_max_qty =
      this.max_qty_field &&
      frappe.meta.has_field(cur_grid.doctype, this.max_qty_field)

    const warehouse_field = this.get_warehouse_field()
    const has_warehouse_field =
      warehouse_field &&
      frappe.meta.has_field(cur_grid.doctype, warehouse_field)

    const warehouse = has_warehouse_field
      ? this.frm.doc.last_scanned_warehouse ||
        this.frm.doc.set_warehouse ||
        default_warehouse
      : null

    console.log(
      `🏥 Debug - warehouse_field: ${warehouse_field}, has_warehouse_field: ${has_warehouse_field}, warehouse: ${warehouse}`
    )
    console.log(
      `🏥 Debug - last_scanned_warehouse: ${this.frm.doc.last_scanned_warehouse}, set_warehouse: ${this.frm.doc.set_warehouse}`
    )

    const matching_row = (row) => {
      const item_match = row.item_code == item_code
      const batch_match =
        !row[this.batch_no_field] || row[this.batch_no_field] == batch_no
      const uom_match = !uom || row[this.uom_field] == uom
      const qty_in_limit =
        flt(row[this.qty_field]) < flt(row[this.max_qty_field])
      const item_scanned = row.has_item_scanned

      let warehouse_match = true
      if (has_warehouse_field && warehouse_field) {
        const current_warehouse = warehouse || null
        const existing_warehouse = row[warehouse_field] || null

        console.log(
          `🏥 Debug - Row ${row.idx} warehouse check: current="${current_warehouse}", existing="${existing_warehouse}"`
        )

        if (current_warehouse && existing_warehouse) {
          warehouse_match = current_warehouse === existing_warehouse
          console.log(`🏥 Debug - Both have warehouses: ${warehouse_match}`)
        } else if (current_warehouse && !existing_warehouse) {
          warehouse_match = false
          console.log(
            `🏥 Debug - Current has warehouse, existing doesn't: ${warehouse_match}`
          )
        } else if (!current_warehouse && existing_warehouse) {
          warehouse_match = false
          console.log(
            `🏥 Debug - Current has no warehouse, existing does: ${warehouse_match}`
          )
        } else {
          warehouse_match = true
          console.log(`🏥 Debug - Both have no warehouse: ${warehouse_match}`)
        }
      }

      const matches =
        item_match &&
        uom_match &&
        warehouse_match &&
        !item_scanned &&
        (!is_batch_no_scan || batch_match) &&
        (!check_max_qty || qty_in_limit)

      if (item_match && !matches) {
        console.log(
          `🏥 Debug - Row ${row.idx} item matches but not selected:`,
          {
            item_match,
            uom_match,
            warehouse_match,
            item_scanned,
            batch_match,
            qty_in_limit,
            current_warehouse: warehouse,
            existing_warehouse: row[warehouse_field],
          }
        )
      }

      return matches
    }

    const items_table = this.frm.doc[this.items_table_name] || []
    return (
      items_table.find(matching_row) || items_table.find((d) => !d.item_code)
    )
  }

  play_success_sound() {
    if (this.enable_sounds && this.success_sound) {
      console.log(`🔊 Playing success sound: ${this.success_sound}`)
      frappe.utils.play_sound(this.success_sound)
    }
  }

  play_fail_sound() {
    if (this.enable_sounds && this.fail_sound) {
      console.log(`🔊 Playing error sound: ${this.fail_sound}`)
      frappe.utils.play_sound(this.fail_sound)
    }
  }

  clean_up() {
    this.scan_barcode_field.set_value("")
    refresh_field(this.items_table_name)
  }

  show_alert(msg, indicator, duration = 3) {
    frappe.show_alert(
      {
        message: msg,
        indicator: indicator,
      },
      duration
    )
  }
}

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
        const s = r.message
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
        }
        console.log(
          `🏥 SurgiShop ERP Scanner: Settings loaded:`,
          window.surgishop.settings
        )

        // Apply global flag to disable serial/batch selector
        if (window.surgishop.settings.disableSerialBatchSelector) {
          frappe.flags.hide_serial_batch_dialog = true
          console.log(
            `🏥 SurgiShop ERP Scanner: Serial/Batch selector dialog DISABLED globally`
          )
        }
      }
    },
  })
}

// Load settings on page load
$(document).ready(() => {
  loadSurgiShopScannerSettings()
})

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
  ]

  if (
    frappe.get_route() &&
    frappe.get_route()[0] === "Form" &&
    doctypes_to_override.includes(frappe.get_route()[1])
  ) {
    const frm = cur_frm
    if (frm && !frm.custom_scanner_attached) {
      frappe.ui.form.on(frappe.get_route()[1], {
        scan_barcode: function (frm) {
          console.log(
            `%c🏥 SurgiShop ERP Scanner: Overriding scan_barcode field for ${frm.doctype}`,
            "color: #4CAF50; font-weight: bold;"
          )

          const opts = frm.events.get_barcode_scanner_options
            ? frm.events.get_barcode_scanner_options(frm)
            : {}
          opts.frm = frm

          const scanner = new surgishop.CustomBarcodeScanner(opts)
          scanner.process_scan().catch((err) => {
            console.error("🏥 SurgiShop ERP Scanner: Scan error:", err)
            frappe.show_alert({
              message: "Barcode scan failed. Please try again.",
              indicator: "red",
            })
          })
        },
      })
      frm.custom_scanner_attached = true
    }
  }
})
