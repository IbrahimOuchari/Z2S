odoo.define('nn_z2s.ProductQtyCountedWidget', function (require) {
    "use strict";

    var basicFields = require('web.basic_fields');
    var fieldRegistry = require('web.field_registry');

    var FloatField = basicFields.FieldFloat;

    var ProductQtyCountedWidget = FloatField.extend({
        // We keep the normal float behavior but listen for input events

        events: _.extend({}, FloatField.prototype.events, {
            'input input': '_onInputChanged',  // input event on input element
        }),

        init: function () {
            this._super.apply(this, arguments);
            // store the last value typed by user
            this._lastValue = null;
        },

        _renderEdit: function () {
            this._super.apply(this, arguments);
            if (this.$input) {
                this._lastValue = this.$input.val();
            }
        },

        _onInputChanged: function (event) {
            var currentVal = this.$input.val();
            // console.log('Typed value:', currentVal);

            // Detect if user typed zero again, even if previous was zero
            if (currentVal === '0' && this._lastValue === '0') {
                // Trigger your refresh logic
                this._triggerRefresh();
            }
            this._lastValue = currentVal;
        },

        _triggerRefresh: function () {
            // Example: Call an RPC to backend to do refresh

            var self = this;
            if (this.record && this.record.res_id) {
                this._rpc({
                    model: this.model,
                    method: 'force_refresh_qty_counted_zero',
                    args: [[this.record.res_id]],
                }).then(function () {
                    // After RPC success, reload the field or the form
                    self.trigger_up('reload');
                });
            }
        },
    });

    fieldRegistry.add('product_qty_counted_widget', ProductQtyCountedWidget);

    return ProductQtyCountedWidget;
});
