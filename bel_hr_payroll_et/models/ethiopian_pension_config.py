from odoo import models, fields

class EthiopianPensionConfig(models.Model):
    _name = 'ethiopian.pension.config'
    _description = 'Ethiopian Pension Configuration'
    _order = 'date_from desc'

    name = fields.Char(string='Rule Name', required=True)
    date_from = fields.Date(string='Effective From', required=True)
    date_to = fields.Date(string='Effective To')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    
    employee_rate = fields.Float(string='Employee Contribution Rate (%)', default=7.0)
    employer_rate = fields.Float(string='Employer Contribution Rate (%)', default=11.0)