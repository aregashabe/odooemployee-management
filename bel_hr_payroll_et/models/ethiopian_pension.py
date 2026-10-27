from odoo import models, fields

class EthiopianPensionConfig(models.Model):
    _name = 'ethiopian.pension.config'
    _description = 'Ethiopian Pension Configuration'
    _order = 'date_from desc, company_id'

    name = fields.Char(string='Description', required=True, default='Standard Pension Configuration')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    
    # Rates
    employee_rate = fields.Float(string='Employee Pension Rate (%)', required=True, default=7.0, help="Standard employee contribution rate (e.g., 7%)")
    employer_rate = fields.Float(string='Employer Pension Rate (%)', required=True, default=11.0, help="Standard employer contribution rate (e.g., 11%)")
    
    # Effective Dates
    date_from = fields.Date(string='Effective From', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='Effective To', help="Leave empty for active/indefinite rules")
    
    active = fields.Boolean(string='Active', default=True)

    _company_date_uniq = models.Constraint(
        'UNIQUE(company_id, date_from)',
        'Only one pension configuration can start on the same date per company!'
    )