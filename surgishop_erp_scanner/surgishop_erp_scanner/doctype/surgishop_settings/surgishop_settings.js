// Copyright (c) 2024, SurgiShop and Contributors
// License: MIT. See license.txt

frappe.ui.form.on('SurgiShop Settings', {
	refresh: function(frm) {
		// Set up button click handler
		frm.fields_dict.generate_trigger_barcodes.$input.on('click', function() {
			generateTriggerBarcodes(frm)
		})
	},

	generate_trigger_barcodes: function(frm) {
		generateTriggerBarcodes(frm)
	}
})

/**
 * Generate printable trigger barcodes in a new window
 * @param {object} frm - The form object
 */
function generateTriggerBarcodes(frm) {
	// Collect all trigger barcode values
	const triggers = [
		{
			label: 'New Line Trigger',
			description: 'Forces next item to be added on a new line',
			value: frm.doc.new_line_trigger_barcode
		},
		{
			label: 'Condition Trigger',
			description: 'Sets condition for the next item scan',
			value: frm.doc.condition_trigger_barcode
		},
		{
			label: 'Quantity Trigger',
			description: 'Prompts for quantity on the next item scan',
			value: frm.doc.quantity_trigger_barcode
		},
		{
			label: 'Delete Row Trigger',
			description: 'Deletes/removes the last scanned row',
			value: frm.doc.delete_row_trigger_barcode
		}
	]

	// Filter out empty triggers
	const activeTriggers = triggers.filter(t => t.value && t.value.trim())

	if (activeTriggers.length === 0) {
		frappe.msgprint({
			title: __('No Trigger Barcodes Configured'),
			message: __('Please configure at least one trigger barcode value before generating.'),
			indicator: 'orange'
		})
		return
	}

	// Generate HTML for print window
	const html = generateBarcodePrintHTML(activeTriggers)

	// Open new window for printing
	const printWindow = window.open('', '_blank', 'width=800,height=600')
	printWindow.document.write(html)
	printWindow.document.close()
}

/**
 * Generate the HTML content for the barcode print page
 * @param {Array} triggers - Array of trigger objects with label, description, value
 * @returns {string} Complete HTML document
 */
function generateBarcodePrintHTML(triggers) {
	const barcodeCards = triggers.map(trigger => `
		<div class="barcode-card">
			<div class="barcode-label">${escapeHtml(trigger.label)}</div>
			<div class="barcode-description">${escapeHtml(trigger.description)}</div>
			<svg class="barcode" data-value="${escapeHtml(trigger.value)}"></svg>
			<div class="barcode-value">${escapeHtml(trigger.value)}</div>
		</div>
	`).join('')

	return `
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>SurgiShop Trigger Barcodes</title>
	<script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.6/dist/JsBarcode.all.min.js"></script>
	<style>
		* {
			box-sizing: border-box;
			margin: 0;
			padding: 0;
		}

		body {
			font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
			background: #f5f5f5;
			padding: 20px;
		}

		.header {
			text-align: center;
			margin-bottom: 30px;
			padding-bottom: 20px;
			border-bottom: 2px solid #0077b6;
		}

		.header h1 {
			color: #0077b6;
			font-size: 24px;
			margin-bottom: 5px;
		}

		.header p {
			color: #666;
			font-size: 14px;
		}

		.barcode-grid {
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
			gap: 20px;
			max-width: 900px;
			margin: 0 auto;
		}

		.barcode-card {
			background: white;
			border-radius: 12px;
			padding: 20px;
			box-shadow: 0 2px 8px rgba(0,0,0,0.1);
			text-align: center;
			border: 2px dashed #ddd;
		}

		.barcode-label {
			font-size: 18px;
			font-weight: 600;
			color: #333;
			margin-bottom: 5px;
		}

		.barcode-description {
			font-size: 12px;
			color: #888;
			margin-bottom: 15px;
		}

		.barcode {
			max-width: 100%;
			height: auto;
		}

		.barcode-value {
			font-family: 'Courier New', monospace;
			font-size: 14px;
			color: #555;
			background: #f8f8f8;
			padding: 5px 10px;
			border-radius: 4px;
			margin-top: 10px;
			display: inline-block;
		}

		.print-button {
			display: block;
			margin: 30px auto;
			padding: 12px 30px;
			background: #0077b6;
			color: white;
			border: none;
			border-radius: 6px;
			font-size: 16px;
			cursor: pointer;
			transition: background 0.2s;
		}

		.print-button:hover {
			background: #005f8a;
		}

		.footer {
			text-align: center;
			margin-top: 30px;
			padding-top: 20px;
			border-top: 1px solid #ddd;
			color: #888;
			font-size: 12px;
		}

		@media print {
			body {
				background: white;
				padding: 10px;
			}

			.print-button {
				display: none;
			}

			.barcode-card {
				box-shadow: none;
				page-break-inside: avoid;
				border: 2px dashed #ccc;
			}

			.header {
				margin-bottom: 20px;
			}

			.footer {
				display: none;
			}
		}
	</style>
</head>
<body>
	<div class="header">
		<h1>🏥 SurgiShop Trigger Barcodes</h1>
		<p>Scan these barcodes to trigger special actions during item scanning</p>
	</div>

	<div class="barcode-grid">
		${barcodeCards}
	</div>

	<button class="print-button" onclick="window.print()">🖨️ Print Barcodes</button>

	<div class="footer">
		Generated by SurgiShop ERP Scanner • ${new Date().toLocaleDateString()}
	</div>

	<script>
		// Generate barcodes after page loads
		document.addEventListener('DOMContentLoaded', function() {
			const svgElements = document.querySelectorAll('.barcode')
			svgElements.forEach(function(svg) {
				const value = svg.getAttribute('data-value')
				if (value) {
					try {
						JsBarcode(svg, value, {
							format: 'CODE128',
							width: 2,
							height: 80,
							displayValue: false,
							margin: 10,
							background: '#ffffff'
						})
					} catch (e) {
						console.error('Failed to generate barcode for:', value, e)
						svg.outerHTML = '<div style="color: red; padding: 20px;">Error generating barcode</div>'
					}
				}
			})
		})
	</script>
</body>
</html>
`
}

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
	if (!text) return ''
	const div = document.createElement('div')
	div.textContent = text
	return div.innerHTML
}

