# SurgiShopERPNext - AI Assistant Instructions

## Project Overview

SurgiShopERPNext is a specialized Frappe/ERPNext app designed to allow expired products in transactions for research purposes. This app focuses on disabling batch expiry validation to enable processing of expired items in medical/surgical inventory management.

## AI Agent Development Rules

The AI agent pair-programming with this repository MUST follow these rules:

1.  **Automatic Cache Busting**: After every modification to a client-side asset (e.g., `.js`, `.css` files) that is referenced in `surgishoperpnext/hooks.py`, the agent MUST automatically increment the version query string for that asset. For example, `.../file.js?v=1.0.1` should become `.../file.js?v=1.0.2`.

2.  **Automatic Git Push**: After every file modification or creation, the agent MUST automatically stage the changes, commit them with a descriptive, conventional commit message, and push the commit to the remote repository's `development` branch.

3.  **Communication of Changes**: All file modifications and code changes must be clearly communicated to the user in natural language, including explanations of what is being changed and why, before or during the process.

## Key Features

### 🔬 Research-Focused Design
- **Batch Expiry Override**: Completely disables batch expiry validation for ALL transactions
- **Expired Item Handling**: Allows processing of expired items for research purposes
- **Comprehensive Coverage**: Handles all major transaction types
- **Proper Restoration**: Restores original validation after processing

### 🏥 Medical Focus
- **Surgical Supply Management**: Specifically designed for medical/surgical inventory
- **Research Capabilities**: Batch expiry override for research purposes
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

### 🔍 Custom Barcode Scanning
- **Custom Override**: Overrides ERPNext's default barcode scanning with custom implementation
- **Enhanced Functionality**: Custom barcode processing with detailed logging
- **API Integration**: Custom API endpoints for barcode scanning
- **Form Integration**: Seamless integration with ERPNext forms

## Project Structure

```
surgishoperpnext/
├── hooks.py                          # Main Frappe app configuration
├── surgishoperpnext/
│   ├── api/
│   │   └── barcode.py                # Custom barcode scanning API
│   ├── overrides/
│   │   └── stock_controller.py       # Batch expiry override logic
│   └── patches/                      # Database migration patches
├── public/js/
│   └── custom-barcode-scanner.js     # Custom barcode scanner override
└── templates/
    └── pages/
```

## Supported Transactions

The batch expiry override functionality is applied to these doctypes:

- **Purchase Receipt** - Goods receipt processing
- **Purchase Invoice** - Purchase invoice processing
- **Stock Entry** - Material transfers and adjustments
- **Stock Reconciliation** - Stock reconciliation
- **Sales Invoice** - Sales invoice processing
- **Delivery Note** - Delivery note processing

## Custom Barcode Scanning

### Override Implementation
- **Custom BarcodeScanner**: Overrides ERPNext's default `erpnext.utils.BarcodeScanner` class
- **Custom API**: Uses `surgishoperpnext.surgishoperpnext.api.barcode.scan_barcode` instead of default
- **Enhanced Logging**: Detailed logging for debugging and monitoring
- **Form Integration**: Seamless integration with ERPNext transaction forms

### How It Works

1. **JavaScript Override**: Custom `BarcodeScanner` class replaces ERPNext's default
2. **API Call**: Calls custom barcode scanning API with enhanced functionality
3. **Form Update**: Updates form with scanned item details
4. **Logging**: Comprehensive logging for debugging

### API Endpoints

#### `scan_barcode(search_value, ctx)`
- **Purpose**: Main barcode scanning function
- **Input**: Barcode value and context
- **Output**: Item details including code, name, UOM, rate, etc.
- **Search Order**: Item Barcode → Serial No → Batch No → Warehouse

#### `get_item_by_barcode(barcode)`
- **Purpose**: Simple barcode lookup
- **Input**: Barcode string
- **Output**: Item details

#### `validate_barcode(barcode)`
- **Purpose**: Validate if barcode exists
- **Input**: Barcode string
- **Output**: Boolean validation result

## Batch Expiry Override

### Research-Focused Design
- **Complete Override**: Disables batch expiry validation for ALL transactions
- **Research Purpose**: Allows processing of expired items for research
- **Comprehensive Coverage**: Handles all major transaction types
- **Proper Restoration**: Restores original validation after processing

### How It Works

1. **Before Validation**: Disables batch expiry validation by monkey-patching `StockController.validate_serialized_batch`
2. **After Processing**: Restores original validation function
3. **On Cancel**: Restores original validation function

### Implementation Details

The override works by:
- Storing the original `validate_serialized_batch` method
- Replacing it with a no-op function during document processing
- Restoring the original method after processing is complete

## Configuration

### hooks.py Configuration
```python
# Custom barcode scanner loading for specific doctypes
doctype_js = {
    "Stock Entry": "/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=1.0.1",
    "Purchase Order": "/assets/surgishoperpnext/js/custom-barcode-scanner.js?v=1.0.1",
    # ... other doctypes
}

# Document event hooks for batch expiry override
doc_events = {
    "Purchase Receipt": {
        "before_validate": "surgishoperpnext.surgishoperpnext.overrides.stock_controller.disable_batch_expiry_validation",
        "after_insert": "surgishoperpnext.surgishoperpnext.overrides.stock_controller.restore_batch_expiry_validation",
        "on_cancel": "surgishoperpnext.surgishoperpnext.overrides.stock_controller.restore_batch_expiry_validation"
    },
    # ... other doctypes
}
```

## Development Guidelines

### Code Style
- **Python**: PEP 8 compliant
- **Error Handling**: Comprehensive try-catch blocks
- **Logging**: Detailed logging for debugging

### Performance Considerations
- **Efficient Override**: Minimal performance impact
- **Memory Management**: Proper cleanup and restoration
- **Error Handling**: Graceful error handling

### Security
- **Input Validation**: Proper validation of document types
- **Error Handling**: Graceful error handling
- **Data Integrity**: Maintains data integrity while allowing expired items

## Testing

### Running Python Tests

The app includes comprehensive unit tests for the barcode scanning and GS1 parsing functionality.

```bash
# Run all tests for the app
bench --site [your-site] run-tests --app surgishoperpnext

# Run specific test module
bench --site [your-site] run-tests surgishoperpnext.surgishoperpnext.api.test_barcode
bench --site [your-site] run-tests surgishoperpnext.surgishoperpnext.api.test_gs1_parser
```

### Running JavaScript Tests

The GS1Parser utility includes browser-based unit tests.

```javascript
// Open browser console and run:
surgishop.runGS1Tests()
```

### Test Coverage

- **Barcode API Tests** (`test_barcode.py`)
  - Valid barcode scanning
  - Invalid barcode handling
  - Barcode validation
  - Context parameter handling
  
- **GS1 Parser Tests** (`test_gs1_parser.py`)
  - Valid GS1 barcode parsing
  - Batch creation and retrieval
  - Invalid input handling
  - Expiry date parsing
  - Whitespace handling
  
- **GS1Parser Utility Tests** (`test-gs1-utils.js`)
  - GS1 string parsing
  - Application Identifier validation
  - Format validation
  - Edge case handling

## Troubleshooting

### Common Issues

#### 1. Override Not Working
- **Check**: Console logs for override function calls
- **Verify**: Document events are properly configured in hooks.py
- **Debug**: Check frappe logs for error messages

#### 2. Validation Not Restored
- **Check**: After processing logs
- **Verify**: Original function is properly stored
- **Debug**: Check for exceptions in restore function

### Debug Commands
```python
# Check if override is active
import frappe
from erpnext.controllers.stock_controller import StockController
print(StockController.validate_serialized_batch)

# Check frappe logs
frappe.logger().info("Checking override status")
```

## Maintenance

### Regular Tasks
- **Version Updates**: Update version numbers in hooks.py
- **Testing**: Regular testing of batch expiry override functionality
- **Logging**: Monitor frappe logs for issues
- **Performance**: Monitor processing times

### Updates
- **Override Logic**: Test batch expiry override after changes
- **Document Events**: Verify document event hooks still work
- **Error Handling**: Test error scenarios

## Support

### Documentation
- **Code Comments**: Comprehensive inline documentation
- **Logging**: Detailed logging for debugging
- **API Documentation**: Well-documented override functions

### Debugging
- **Frappe Logs**: Check frappe logs for detailed information
- **Console Logs**: Monitor console for override status
- **Error Handling**: Test error scenarios

## Version Management

### Automatic Version Bumping
- **AI Assistant Responsibility**: The AI assistant will automatically increment the version number (x.y.n) where n is the patch version before every git push
- **Version Format**: Semantic versioning (x.y.z) where:
  - x = Major version (breaking changes)
  - y = Minor version (new features)
  - z = Patch version (bug fixes)
- **Files Updated**: 
  - `surgishoperpnext/__init__.py` - Main version
  - `surgishoperpnext/hooks.py` - JavaScript version numbers
  - `INSTRUCTIONS.md` - Documentation version

### Manual Version Bumping
If manual version bumping is needed:
1. Edit `surgishoperpnext/__init__.py` and update `__version__`
2. Update version numbers in `surgishoperpnext/hooks.py` (v=1.0.x)
3. Update version in `INSTRUCTIONS.md`
4. Commit and push changes

## Version Information

- **Current Version**: 0.3.1
- **Python Requirements**: >=3.10
- **Frappe Compatibility**: ~15.0.0
- **License**: MIT

## Contact

- **Developer**: SurgiShop
- **Email**: Arthur.Borges@SurgiShop.com
- **Repository**: GitHub - surgishoperpnext

---

**Note**: This app is specifically designed for research purposes to allow processing of expired items. The batch expiry override is intentional for research purposes and should be used responsibly.

## Changelog

### Version 0.3.1 (Critical Fix - Auto-Parse Prevention)
**Fixed Serial/Batch Dialog Auto-Parsing Issue**

#### 🐛 Critical Fix
- **Fixed: Dialog auto-parsing on open** - The serial/batch bundle picker was automatically parsing GS1 barcodes when the dialog opened, even without user input
- **Root Cause**: The `scan_batch_no` field retained values from previous scans, triggering the `onchange` handler immediately when attached
- **Solution**: Clear the field value before attaching the `onchange` handler to prevent auto-trigger

#### 🔧 Technical Changes
- Added `scanField.set_value("")` before `scanField.df.onchange` assignment in `custom-serial-batch-selector.js`
- Ensures clean state when dialog opens
- Prevents unwanted parsing and API calls

#### ✅ Result
- Dialog opens cleanly without automatic parsing
- GS1 parsing only triggers when user actually scans a barcode
- Improved user experience and reduced unnecessary API calls

---

### Version 0.1.19 (Serial/Batch Dialog Enhancement)
**Enhanced Serial/Batch Dialog with Item Context Display**

#### 🎯 New Features
- **Item Code Display** - Dialog now shows the item code and name at the top
- **Enhanced Dialog Title** - Title includes item code and name for better context
- **Read-Only Item Field** - Displays "ITEM-CODE - Item Name" format for clarity
- **Context-Aware Messages** - Success messages include item code for reference

#### 🔧 Dialog Improvements
- **Field Ordering** - Item display field appears first, followed by GS1 scan field
- **Better UX** - Users can easily identify which item they're working with
- **Consistent Context** - All dialog interactions maintain item context
- **Debug Logging** - Added console logging for troubleshooting

#### ✅ User Experience
- ✓ **Clear Item Identification** - No confusion about which item is being processed
- ✓ **Enhanced Workflow** - Better context when adding serial/batch numbers
- ✓ **Professional Interface** - More informative and user-friendly dialog
- ✓ **Consistent Messaging** - All feedback includes item context

---

### Version 0.1.3 (Sound Feedback Enhancement)
**Added Audio Feedback for Barcode Scanning**

#### 🔊 New Features
- **Success Sound** - Plays when item is added to list or quantity is incremented
- **Error Sound** - Plays when barcode scan fails or item not found
- **Enabled by Default** - Sounds are now automatically enabled for better UX

#### 🎵 Sound Implementation
- **Success Sound**: Uses Frappe's built-in `"submit"` sound (pleasant beep)
- **Error Sound**: Uses Frappe's built-in `"error"` sound (alert tone)
- **Configurable**: Can be customized via `play_success_sound` and `play_fail_sound` options
- **Console Logging**: Added 🔊 emoji logging to indicate when sounds play

#### ✅ When Sounds Play
- ✓ **Success Sound**: 
  - New item added to items table
  - Item quantity incremented
  - Batch/serial number successfully assigned
- ✗ **Error Sound**:
  - Barcode not found
  - Item doesn't exist
  - GS1 parsing fails
  - API errors
  - Invalid scan

#### 🎯 User Experience
- Immediate audio feedback confirms scan success/failure
- No need to look at screen to know if scan was successful
- Faster scanning workflow with auditory confirmation
- Reduces data entry errors

---

### Version 0.1.2 (Critical Fix - GS1Parser Loading)
**Hot Fix for GS1Parser Not Loading**

#### 🐛 Critical Fix
- **Fixed: GS1Parser not loaded in browser** - `gs1-utils.js` was not being loaded globally
- **Loading Order Issue Resolved** - `custom-barcode-scanner.js` was loading before `gs1-utils.js` dependency

#### 🔧 Configuration Changes
- Moved `gs1-utils.js` to global `app_include_js` (was only in `doctype_js`)
- **Load order now correct**: `gs1-utils.js` → `custom-barcode-scanner.js`
- Ensures `window.surgishop.GS1Parser` is available when barcode scanner initializes

#### ✅ Result
- GS1 barcodes with alphanumeric lot numbers now scan correctly
- Error `"GS1Parser not loaded! Make sure gs1-utils.js is included."` resolved
- Barcode `012070503100301617251220103IAIDP06` now works in all forms

---

### Version 0.1.1 (GS1 Parser Enhancement - bark.js Style)
**Enhanced GS1 Barcode Parsing**

#### 🎯 Critical Fix
- **Fixed GS1 Parser to support alphanumeric lot numbers** - Previous version only accepted numeric-only barcodes
- Real-world barcode now supported: `012070503100301617251220103IAIDP06` (lot: `3IAIDP06`)

#### 🏗️ Parser Rewrite (Inspired by bark.js)
- **Complete rewrite of GS1Parser** using Application Identifier (AI) definitions
- **AI Definition Table** with fixed/variable length and numeric/alphanumeric type support
- **Intelligent variable-length field parsing** - automatically detects next AI or end of string
- **Support for multiple GS1 AIs**:
  - AI 01: GTIN (14 digits, numeric)
  - AI 10: LOT (variable, alphanumeric) ← **Now supports alphanumeric!**
  - AI 11: Production Date (6 digits, numeric)
  - AI 13: Packaging Date (6 digits, numeric)
  - AI 15: Best Before (6 digits, numeric)
  - AI 17: Expiry Date (6 digits, numeric)
  - AI 21: Serial Number (variable, alphanumeric)
  - AI 30: Count (variable, numeric)
  - AI 37: Quantity (variable, numeric)
  - AI 310: Net Weight in KG (6 digits, numeric)

#### ✅ Enhanced Testing
- Added test case for alphanumeric lot numbers (`testValidGS1ParseAlphanumericLot`)
- Added `testStringifyGS1` for round-trip conversion
- Removed obsolete `testInvalidGS1NonNumeric` (now valid with alphanumeric support)

#### 📝 New Features
- `GS1Parser.stringify()` - Convert parsed object back to raw GS1 string
- `GS1Parser.format()` - Enhanced to handle all supported AIs
- Better AI detection (checks 3-digit AIs before 2-digit AIs)

#### 🐛 Bug Fixes
- Fixed: Barcode `012070503100301617251220103IAIDP06` now parses correctly
- Fixed: Variable-length fields now properly detect the next AI
- Fixed: Alphanumeric characters in lot numbers no longer cause parse failure

#### 📚 Documentation
- Updated comments to reference bark.js inspiration
- Added comprehensive AI definition documentation
- Improved logging with per-AI parse status

---

### Version 0.1.0 (Code Quality & Testing Release)
**Major Refactoring and Improvements**

#### 🔧 Critical Fixes
- Fixed missing import in `gs1_parser.py` - added `from frappe import _`
- Fixed JavaScript scoping error in `custom-barcode-scanner.js` - `prepare_item_for_scan()` now returns a proper Promise
- Implemented thread-safe monkey-patching in `stock_controller.py` using `frappe.local` instead of global variables

#### 🏗️ Architecture Improvements
- **Extracted GS1 parsing to shared utility** - Created `gs1-utils.js` to eliminate code duplication
- **Centralized GS1Parser class** with constants, validation, and formatting methods
- Both `custom-barcode-scanner.js` and `custom-serial-batch-selector.js` now use the shared GS1Parser

#### ✅ Testing & Quality
- Added comprehensive unit tests for barcode scanning API (`test_barcode.py`)
- Added comprehensive unit tests for GS1 parser API (`test_gs1_parser.py`)
- Added JavaScript unit tests for GS1Parser utility (`test-gs1-utils.js`)
- Test coverage for edge cases, error handling, and input validation

#### 🛡️ Error Handling
- Enhanced error handling in `gs1_parser.py` with comprehensive try-catch blocks
- Added input validation and sanitization (whitespace stripping)
- Added item validation (disabled check, batch_no support check)
- Improved error logging with `frappe.log_error()` for full stack traces
- Better error messages for users

#### 📝 Code Quality
- Added comprehensive docstrings to all functions
- Improved logging throughout with clear context
- Added type hints and parameter documentation
- Better code organization and maintainability
- Removed duplicate code (DRY principle)

#### 🔢 Version Alignment
- Aligned all version numbers to 0.1.0 across the codebase
- Updated `__init__.py`, `hooks.py`, and documentation
- Consistent versioning for cache busting on JavaScript assets

#### 📚 Documentation
- Updated INSTRUCTIONS.md with new version information
- Documented all fixes and improvements
- Added security notes for permission bypass in batch creation

---

### Previous Versions (Historical)

### Version 0.4.2 (GS1 Parser Correction)
- Switched to gs1-parser library from CDN for accurate GS1 parsing.

### Version 0.4.1 (GS1 Library Fix)
- Fixed loading to prevent 'not defined' errors.

### Version 0.4.0 (GS1 Parsing Improvement)
- Integrated library for robust GS1 barcode parsing.

### Version 0.3.0 (Barcode Scanning Enhancements)
- Implemented custom GS1 barcode parsing for raw formats without parentheses.
- Added robust override for the scan_barcode field in transaction forms (e.g., Purchase Receipt) using frappe.ui.form.on and router events.
- Fixed uncaught promise rejections with .catch() handling and user-friendly alerts.
- Cleaned up duplicate console logs by adding a flag to prevent multiple handler attachments.
- Resolved variable scoping issues in GS1 parser.
- Enhanced logging for parsed GTIN, lot, and expiry details.
- Overall improvements to barcode scanning reliability for research-focused inventory management, including batch creation via API.