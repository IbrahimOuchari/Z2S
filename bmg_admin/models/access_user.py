from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


# Ajouter groupe exclu dans groupe menu

class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    excluded_group_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="ir_ui_menu_excluded_group_rel",
        column1="menu_id",
        column2="gid",
        string="Groupes Exclus",
    )

    @api.model
    @tools.ormcache("frozenset(self.env.user.groups_id.ids)", "debug")
    def _visible_menu_ids(self, debug=False):
        visible = super()._visible_menu_ids(debug=debug)
        context = {"ir.ui.menu.full_list": True}
        menus = self.with_context(context).browse(visible)
        groups = self.env.user.groups_id
        visible = menus - menus.filtered(lambda menu: menu.excluded_group_ids & groups)
        return set(visible.ids)

#masquer menu par user
class Menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super(Menu, self)._visible_menu_ids(debug)
        if self.env.user.hide_menu_access_ids and not self.env.user.has_group('base.group_system'):
            for rec in self.env.user.hide_menu_access_ids:
                menus.discard(rec.id)
            return menus
        return menus


class ResUsers(models.Model):
    _inherit = 'res.users'

    hide_menu_access_ids = fields.Many2many('ir.ui.menu', 'ir_ui_hide_menu_rel', 'uid', 'menu_id',
                                            string='Masquer Accès Menu')
