from odoo import models, fields

class BelBonusType(models.Model):
    _name = 'bel.bonus.type'
    _description = 'Bonus and Incentive Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Bonus Type Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    description = fields.Text(string='Description')
    category = fields.Selection([
        ('performance', 'Performance Bonus'),
        ('annual', 'Annual Bonus'),
        ('holiday', 'Holiday Bonus'),
        ('attendance', 'Attendance Incentive'),
        ('productivity', 'Productivity Bonus'),
        ('sales', 'Sales Incentive'),
        ('project', 'Project Completion Bonus'),
        ('recognition', 'Employee Recognition Bonus'),
        ('other', 'Other'),
    ], string='Bonus Category', required=True, default='performance', tracking=True)