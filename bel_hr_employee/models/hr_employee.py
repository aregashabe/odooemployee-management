from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ethiopian_employee_id = fields.Char(
        string='Ethiopian Employee ID',
        copy=False,
    )

    employment_category_id = fields.Many2one(
        'bel.hr.employment.category',
        string='Employment Category',
        tracking=True,
        check_company=True,
    )

    employee_grade_id = fields.Many2one(
        'bel.hr.employee.grade',
        string='Employee Grade / Level',
        check_company=True,
    )


    ethiopian_employment_start_date = fields.Date(
        string='Employment Start Date',
        tracking=True,
    )

    original_joining_date = fields.Date(
        string='Original Joining Date',
        tracking=True,
    )

    probation_start_date = fields.Date(
        string='Probation Start Date',
    )

    probation_end_date = fields.Date(
        string='Probation End Date',
    )

    pension_eligible = fields.Boolean(
        string='Pension Eligible',
        default=False,
        groups="hr.group_hr_user",
    )

    pension_scheme = fields.Selection(
        [
            ('private', 'Private Organization Scheme'),
            ('public', 'Public Sector Scheme'),
            ('other', 'Other'),
        ],
        string='Pension Scheme',
        groups="hr.group_hr_user"
    )

    ethiopian_tax_id = fields.Char(
        string='Tax Identification Number',
        copy=False,
        groups="hr.group_hr_user"
    )

