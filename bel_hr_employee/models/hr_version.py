
from odoo import fields, models


class HrVersion(models.Model):
    _inherit = 'hr.version'

    bel_employment_category_id = fields.Many2one(
        'bel.hr.employment.category',
        string='Employment Category',
        check_company=True,
    )

    bel_probation_start_date = fields.Date(
        string='Probation Start Date',
    )

    bel_pension_eligible = fields.Boolean(
        string='Pension Eligible',
        default=False,
        groups="hr.group_hr_user",
    )

    bel_pension_scheme = fields.Selection(
        [
            ('private', 'Private Organization Scheme'),
            ('public', 'Public Sector Scheme'),
            ('other', 'Other'),
        ],
        string='Pension Scheme',
        groups="hr.group_hr_user"
    )

    bel_contract_reference = fields.Char(
        string='BelTech Contract Reference',
        copy=False,
    )
