import logging
import random
import string

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    """Implement company wide unique identification number."""

    _inherit = "hr.employee"

    identification_id = fields.Char(string="Matricule N° ", copy=False)

    matricule_cnss = fields.Char('Matricule CNSS', size=10)
    num_cin = fields.Char('CIN', size=8)
    date_cin = fields.Date('Délivrée Le')
    banque = fields.Char('Banque')
    compte_banque = fields.Char('Compte Bancaire', size=20)


    _sql_constraints = [
        (
            "identification_id_uniq",
            "unique(identification_id)",
            "La matricule employé doit être unique !",
        ),
    ]

    @api.model
    def _generate_identification_id(self):
        """Generate a random employee identification number"""
        company = self.env.user.company_id

        steps = 0
        for _retry in range(50):
            employee_id = False
            if company.employee_id_gen_method == "sequence":
                if not company.employee_id_sequence:
                    _logger.warning("Aucune séquence configurée pour la génération d'ID d'employé")
                    return employee_id
                employee_id = company.employee_id_sequence.next_by_id()
            elif company.employee_id_gen_method == "random":
                employee_id_random_digits = company.employee_id_random_digits
                rnd = random.SystemRandom()
                employee_id = "".join(
                    rnd.choice(string.digits) for x in range(employee_id_random_digits)
                )

            if self.search_count([("identification_id", "=", employee_id)]):
                steps += 1
                continue

            return employee_id

        raise UserError(
            _("Impossible de générer un ID d'employé unique en %d étapes.") % (steps,)
        )

    @api.model
    def create(self, vals):
        if not vals.get("identification_id"):
            vals["identification_id"] = self._generate_identification_id()
        return super(HrEmployee, self).create(vals)

class ResCompany(models.Model):
    _inherit = "res.company"

    employee_id_gen_method = fields.Selection(
        selection=[
            ("random", "Aléatoire"),
            ("sequence", "Séquence"),
        ],
        string="Méthode de Génération",
        default="sequence",
    )
    employee_id_random_digits = fields.Integer(
        string="# de chiffres", default=4, help="Nombre de chiffres dans l'identifiant de l'employé"
    )
    employee_id_sequence = fields.Many2one(
        comodel_name="ir.sequence",
        string="Séquence d'Identification",
        help="Modèle à utiliser pour la génération de l'identifiant de l'employé",
    )

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    employee_id_gen_method = fields.Selection(
        related="company_id.employee_id_gen_method",
        readonly=False,
        default=lambda self: self._default_id_gen_method(),
    )
    employee_id_random_digits = fields.Integer(
        related="company_id.employee_id_random_digits",
        readonly=False,
        default=lambda self: self._default_id_random_digits(),
    )
    employee_id_sequence = fields.Many2one(
        "ir.sequence",
        related="company_id.employee_id_sequence",
        readonly=False,
        default=lambda self: self._default_id_sequence(),
    )

    def _default_id_gen_method(self):
        gen_method = self.env.user.company_id.employee_id_gen_method
        if not gen_method:
            gen_method = self.env["res.company"].default_get(
                ["employee_id_gen_method"]
            )["employee_id_gen_method"]
        return gen_method

    def _default_id_random_digits(self):
        digits = self.env.user.company_id.employee_id_random_digits
        if not digits:
            digits = self.env["res.company"].default_get(["employee_id_random_digits"])[
                "employee_id_random_digits"
            ]
        return digits

    def _default_id_sequence(self):
        sequence = self.env.user.company_id.employee_id_sequence
        if not sequence:
            sequence = self.env.ref("bmg_hr.seq_hr_employee_id")
        return sequence and sequence.id or False
