from odoo import models, fields

class BelBonusPolicy(models.Model):
    _name = 'bel.bonus.policy'
    _description = 'Bonus Policy Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Policy Name', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    bonus_type_id = fields.Many2one('bel.bonus.type', string='Bonus Type', required=True, tracking=True)
    effective_date = fields.Date(string='Effective Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    
    # Eligibility & Rules
    min_service_months = fields.Integer(string='Minimum Service Period (Months)', default=0)
    min_performance_score = fields.Float(string='Minimum Performance Score')
    calculation_method = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Salary'),
        ('performance', 'Performance-Based'),
        ('target', 'Target-Based'),
        ('manual', 'Manual Bonus'),
    ], string='Calculation Method', required=True, default='fixed', tracking=True)
    
    fixed_amount = fields.Float(string='Fixed Amount')
    percentage_rate = fields.Float(string='Percentage Rate (%)')
    max_bonus_limit = fields.Float(string='Maximum Bonus Limit')
    frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annually'),
        ('annual', 'Annually'),
        ('ad_hoc', 'Ad-hoc'),
    ], string='Bonus Frequency', default='annual', required=True)