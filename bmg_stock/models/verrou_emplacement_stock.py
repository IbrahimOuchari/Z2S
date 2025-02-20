
from odoo import _, fields, models, api
from odoo.exceptions import UserError, ValidationError


class StockLocation(models.Model):
    _inherit = "stock.location"

    block_stock_entrance = fields.Boolean(string="Bloquer les entrées de stock",
        help="si cette case est cochée, mettre du stock sur cet emplacement ne sera pas "
         "autorisé. Habituellement utilisé pour un emplacement virtuel qui a "
         "les enfants."
    )

    # Raise error if the location that you're trying to block
    # has already got quants
    def write(self, values):
        res = super().write(values)

        if "block_stock_entrance" in values and values["block_stock_entrance"]:
            # Unlink zero quants before checking
            # if there are quants on the location
            self.env["stock.quant"]._unlink_zero_quants()
            if self.mapped("quant_ids"):
                raise UserError(
                    _(
                        "Il est impossible d'interdire cet emplacement car il contient déjà des produits."
                    )
                )
        return res


class StockQuant(models.Model):
    _inherit = "stock.quant"

    # Raise an error when trying to change a quant
    # which corresponding stock location is blocked
    @api.constrains("location_id")
    def check_location_blocked(self):
        for record in self:
            if record.location_id.block_stock_entrance:
                raise ValidationError(
                    _(
                        "L'emplacement %s est bloqué et ne peut "
                         "pas être utilisé pour déplacer le produit %s"
                    )
                    % (record.location_id.display_name, record.product_id.display_name)
                )
