odoo.define('stock.InventoryLineRedirectController', function (require) {
    "use strict";

    const ListController = require('web.ListController');

    const InventoryLineRedirectController = ListController.extend({
        events: Object.assign({}, ListController.prototype.events, {
            'click .o_button_redirect_inventory': '_onRedirectClick',
        }),

        _onRedirectClick: function () {
            console.log("🚀 Redirect button clicked!");

            // You could use a hardcoded res_id for testing or from context
            const inventoryId = this.renderer.state.context.active_id || null;

            if (inventoryId) {
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'stock.inventory',
                    view_mode: 'form',
                    res_id: inventoryId,
                    target: 'current',
                });
            } else {
                this.do_notify("Inventaire manquant", "Aucun ID d'inventaire trouvé.");
            }
        },
    });

    return InventoryLineRedirectController;
});
