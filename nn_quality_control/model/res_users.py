from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)
class ResUsers(models.Model):
    """
    Model to handle hiding specific menu items for certain users.
    """
    _inherit = 'res.users'

    def write(self, vals):
        """
        Write method for the ResUsers model.
        Restrict or remove menu items based only on the 'in_group_126' field.
        """
        _logger.info("Starting write method for user(s), vals: %s", vals)

        # Check if the 'in_group_126' field is present in the vals
        if 'in_group_126' in vals:
            _logger.info("Field 'in_group_126' found in vals. Value: %s", vals['in_group_126'])

            # Iterate through the users being updated
            for record in self:
                # Get the default menu items to hide
                menu_items = self._default_hide_menu()
                _logger.info("Menu items to hide: %s", [menu.name for menu in menu_items])

                if vals['in_group_126']:
                    # If 'in_group_126' is True, restrict the menu for the user
                    _logger.info("'in_group_126' is True, restricting menus for user '%s'", record.name)
                    for menu in menu_items:
                        _logger.info("Restricting menu '%s' for user '%s'", menu.name, record.name)
                        menu.write({
                            'restrict_user_ids': [(4, record.id)]  # Add user to restricted list
                        })
                else:
                    # If 'in_group_126' is False, remove the restriction for the user
                    _logger.info("'in_group_126' is False, removing menu restrictions for user '%s'", record.name)
                    for menu in menu_items:
                        _logger.info("Removing restriction from menu '%s' for user '%s'", menu.name, record.name)
                        menu.write({
                            'restrict_user_ids': [(3, record.id)]  # Remove user from restricted list
                        })

        # Call the super method to apply changes (ensuring it's saved to the database)
        res = super(ResUsers, self).write(vals)
        _logger.info("Write operation completed. Result: %s", res)

        return res

    def _default_hide_menu(self):
        """
        Default method to return the menu items that should be hidden by default.
        """
        return self.env['ir.ui.menu'].search([
            ('name', 'not in', ['Discuss','Notes','Gestion qualité']),
            ('parent_id', '=', False)  # Only top-level menus

        ])

    hide_menu_ids = fields.Many2many(
        'ir.ui.menu', string="Hidden Menu",
        store=True, help='Select menu items that need to be hidden for this user.',
        default=_default_hide_menu  # Set default menu items to be hidden
    )
    def _get_is_admin(self):
        """
        Compute method to check if the user is an admin.
        The Hide specific menu tab will be hidden for the Admin user form.
        """
        for rec in self:
            rec.is_admin = False
            if rec.id == self.env.ref('base.user_admin').id:
                rec.is_admin = True
    is_admin = fields.Boolean(compute=_get_is_admin, string="Is Admin",
                              help='Check if the user is an admin.')


class IrUiMenu(models.Model):
    """
    Model to restrict the menu for specific users.
    """
    _inherit = 'ir.ui.menu'

    restrict_user_ids = fields.Many2many(
        'res.users', string="Restricted Users",
        help='Users restricted from accessing this menu.')
