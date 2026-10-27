from odoo import models, fields

class HrOffboardingType(models.Model):
    _name = 'hr.offboarding.type'
    _description = 'Separation Type Configuration'
    _order = 'sequence, id'

    name = fields.Char(string='Separation Type', required=True, translate=True)
    sequence = fields.Integer(default=10)
    category = fields.Selection([
        ('resignation', 'Voluntary Resignation'),
        ('retirement', 'Retirement'),
        ('contract_end', 'End of Fixed-Term Contract'),
        ('mutual', 'Mutual Separation'),
        ('termination', 'Employer-Initiated Termination'),
        ('redundancy', 'Redundancy'),
        ('death', 'Death'),
        ('other', 'Other'),
    ], string='Category', required=True, default='resignation')
    
    notice_period_days = fields.Integer(string='Standard Notice Period (Days)', default=30)
    requires_severance = fields.Boolean(string='Eligible for Severance Pay', default=False)
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')