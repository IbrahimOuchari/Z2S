odoo.define('nn_stock_zero_qty_adjustment.inventory_line_redirect', function (require) {
    "use strict";

    const ListController = require('web.ListController');
    const ListView = require('web.ListView');
    const viewRegistry = require('web.view_registry');

    const InventoryLineRedirectController = ListController.extend({
        start: function () {
            console.log("✅ Custom controller loaded");
            return this._super.apply(this, arguments);
        },
    });

    const InventoryLineRedirectView = ListView.extend({
        config: Object.assign({}, ListView.prototype.config, {
            Controller: InventoryLineRedirectController, // 🚨 Must be defined
        }),
    });

    viewRegistry.add('inventory_line_redirect_view', InventoryLineRedirectView); // 🚨 js_class must match this

    return InventoryLineRedirectView; // ✅ Safest to also return the view
});
