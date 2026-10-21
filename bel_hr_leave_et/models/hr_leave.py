from odoo import models, fields

class BelHrLeave(models.Model):
    _name = 'bel.hr.leave'
    _description = 'BelTech Ethiopian Leave Management'

    name = fields.Char(string='Description', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date_from = fields.Datetime(string='Start Date', required=True)
    date_to = fields.Datetime(string='End Date', required=True)
    number_of_days = fields.Float(string='Number of Days', default=1.0)
    is_unpaid = fields.Boolean(string='Unpaid Leave', default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Approved'),
        ('refused', 'Refused')
    ], string='Status', default='draft')