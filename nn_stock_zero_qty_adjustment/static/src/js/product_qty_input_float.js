odoo.define('your_module.product_qty_force_update_widget', function (require) {
    "use strict";

    const FieldFloat = require('web.basic_fields').FieldFloat;
    const fieldRegistry = require('web.field_registry');
    const rpc = require('web.rpc');

    const ProductQtyForceUpdateWidget = FieldFloat.extend({
        className: 'o_field_product_qty_force_update',

        events: _.extend({}, FieldFloat.prototype.events, {
            'input input': '_onInputForceUpdate',
        }),

        _renderEdit: function () {
            let value = this.value;
            if (value === 0 || value === false) {
                value = '';
            }
            this.$el.html('');
            this.$input = $('<input>', {
                type: 'text',
                class: 'o_input',
                value: value,
                placeholder: "Tapez une quantité",
            });
            this.$el.append(this.$input);
        },

        async _onInputForceUpdate(ev) {
            const val = ev.target.value;

            if (val === '') {
                this._setValue("0");
            } else if (!isNaN(parseFloat(val))) {
                this._setValue(val);
            } else {
                // invalid input, ignore
                return;
            }

            if (!this.record || !this.record.id) {
                return;
            }

            const realValue = parseFloat(val) || 0;
            const dummyValue = 0.0000001;

            try {
                // First write dummy value to force change detection
                await rpc.query({
                    model: 'stock.inventory.line',
                    method: 'write',
                    args: [[this.record.id], {product_qty_counted: dummyValue}],
                });
                console.log(`Dummy update applied: ${dummyValue}`);

                // Then write the real value right after
                await rpc.query({
                    model: 'stock.inventory.line',
                    method: 'write',
                    args: [[this.record.id], {product_qty_counted: realValue}],
                });
                console.log(`Real value updated: ${realValue}`);

                // Optionally, refresh record to update local cache
                await this.record.reload();

            } catch (err) {
                console.error("Error forcing product_qty_counted update:", err);
            }
        },
    });

    fieldRegistry.add('product_qty_force_update', ProductQtyForceUpdateWidget);
});
