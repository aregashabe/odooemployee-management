
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BelHrEmployeeGrade(models.Model):
    _name = 'bel.hr.employee.grade'
    _description = 'BelTech Employee Grade'
    _order = 'sequence, name'

    name = fields.Char(
        string='Grade Name',
        required=True,
    )

    code = fields.Char(
        string='Grade Code',
        required=True,
    )

    sequence = fields.Integer(
        default=10,
    )

    description = fields.Text(
        string='Description',
    )

    use_salary_band = fields.Boolean(
        string='Use Salary Band',
        default=False,
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Currency',
        readonly=True,
    )

    salary_min = fields.Monetary(
        string='Minimum Salary',
        currency_field='currency_id',
    )

    salary_max = fields.Monetary(
        string='Maximum Salary',
        currency_field='currency_id',
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
        'The grade code must be unique within a company.',
    )

    @api.constrains('use_salary_band', 'salary_min', 'salary_max')
    def _check_salary_band(self):
        for record in self:
            if not record.use_salary_band:
                continue

            if record.salary_min < 0 or record.salary_max < 0:
                raise ValidationError(
                    'Salary band amounts cannot be negative.'
                )

            if record.salary_max < record.salary_min:
                raise ValidationError(
                    'Maximum salary must be greater than or equal '
                    'to minimum salary.'
                )
