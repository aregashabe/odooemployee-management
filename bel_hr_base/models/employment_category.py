
from odoo import fields, models


class BelHrEmploymentCategory(models.Model):
    _name = 'bel.hr.employment.category'
    _description = 'BelTech Employment Category'
    _order = 'name'

    name = fields.Char(
        string='Category Name',
        required=True,
    )

    code = fields.Char(
        string='Code',
        required=True,
    )

    description = fields.Text(
        string='Description',
    )

    requires_end_date = fields.Boolean(
        string='Requires Contract End Date',
        default=False,
    )

    probation_required = fields.Boolean(
        string='Probation Required',
        default=False,
    )

    active = fields.Boolean(
        default=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    _code_company_unique = models.Constraint(
        'UNIQUE(code, company_id)',
        'The category code must be unique within a company.',
    )
