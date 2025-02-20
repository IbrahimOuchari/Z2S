from odoo import _, api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools import config, float_compare


class ProductCategory(models.Model):
    _inherit = "product.category"

    allow_negative_stock = fields.Boolean(
        default=False,
        string="Autoriser le stock négatif",
        help="Autoriser les niveaux de stock négatifs pour les produits stockables "
             "rattaché à cette catégorie. Les options ne s'appliquent pas aux produits "
             "attachés aux sous-catégories de cette catégorie.",
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_negative_stock = fields.Boolean(
        default=False,
        string="Autoriser le stock négatif",
        help="Si cette option n'est pas active sur ce produit ni sur son "
             "catégorie de produit et que ce produit est un produit stockable, "
             "alors la validation des mouvements de stock liés sera bloquée si "
             "le niveau de stock devient négatif avec le mouvement de stock.",
    )


class StockLocation(models.Model):
    _inherit = "stock.location"

    allow_negative_stock = fields.Boolean(
        default=False,
        string="Autoriser le stock négatif",
        help="Autoriser les niveaux de stock négatifs pour les produits stockables dans cet emplacement",
    )


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("product_id", "quantity")
    def check_negative_qty(self):
        p = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        check_negative_qty = (
                                     config["test_enable"] and self.env.context.get("test_stock_no_negative")
                             ) or not config["test_enable"]
        if not check_negative_qty:
            return

        for quant in self:
            disallowed_by_product = (
                    not quant.product_id.allow_negative_stock
                    and not quant.product_id.categ_id.allow_negative_stock
            )
            disallowed_by_location = not quant.location_id.allow_negative_stock
            if (
                    float_compare(quant.quantity, 0, precision_digits=p) == -1
                    and quant.product_id.type == "product"
                    and quant.location_id.usage in ["internal", "transit"]
                    and disallowed_by_product
                    and disallowed_by_location
            ):
                msg_add = ""
                if quant.lot_id:
                    msg_add = _(" lot '%s'") % quant.lot_id.name_get()[0][1]
                raise ValidationError(
                    _(
                        "Vous ne pouvez pas valider cette opération de stock car le "
                        "niveau de stock du produit '%s'%s deviendrait négatif "
                        "(%s) dans l'emplacement du stock '%s' et le stock négatif est "
                        "non autorisé pour ce produit et/ou cet emplacement."
                    )
                    % (
                        quant.product_id.display_name,
                        msg_add,
                        quant.quantity,
                        quant.location_id.complete_name,
                    )
                )
