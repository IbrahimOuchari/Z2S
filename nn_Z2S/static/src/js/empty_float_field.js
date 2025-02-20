odoo.define('nn_Z2S.empty_float_field', function (require) {
    "use strict";

    var fieldRegistry = require('web.field_registry');
    var FieldFloat = require('web.basic_fields').FieldFloat;

    // Custom widget for handling empty float fields display
    var FieldEmptyFloat = FieldFloat.extend({

        // Format number to remove excessive decimals
        _formatValue: function(value) {
            if (value === null || value === undefined) {
                return '';
            }
            // Round to 2 decimal places and remove trailing zeros
            return Number(parseFloat(value).toFixed(2))
                .toString()
                // Add % sign if the value is a percentage
                + (this.field.string.toLowerCase().includes('percentage') ? '%' : '');
        },

        // Render the field: display it as an input field
        _render: function () {
            var value = this.value;  // Get the value of the field
            // Display the field as empty if the value is 0
            if (value === 0.0 || value === undefined || value === null) {
                this.$el.html('<input type="text" class="form-control" value="" />');
            } else {
                var formattedValue = this._formatValue(value);
                this.$el.html('<input type="text" class="form-control" value="' + formattedValue + '" />');
            }

            // Attach the input event to handle the value change
            var $input = this.$el.find('input');
            if ($input.length) {
                $input.on('input', this._onInputChange.bind(this));
            } else {
                console.error('Input element not found!');
            }
        },

        // Handle input change: only modify display value (leave the default to Python)
        _onInputChange: function (ev) {
            var value = ev.target.value;

            // Remove % sign if present before parsing
            value = value.replace('%', '').trim();

            // If the input is empty, let Python handle it as 0.0
            if (value === '') {
                this.value = null;  // We leave the value empty and rely on Python to set it to 0.0
            } else {
                this.value = parseFloat(value) || null;  // Otherwise, parse the float, or set it as null if invalid
            }

            // Update the input field's displayed value
            this.$el.find('input').val(this._formatValue(this.value));
        }
    });

    // Register the custom widget in Odoo's field registry
    fieldRegistry.add('empty_float_field', FieldEmptyFloat);
});