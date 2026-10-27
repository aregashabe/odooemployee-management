from odoo import models, fields

class BelHrOvertime(models.Model):
    _name = 'bel.hr.overtime'
    _description = 'BelTech Overtime Management'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Date(string='Overtime Date', required=True, default=fields.Date.context_today)
    hours = fields.Float(string='Overtime Hours', required=True)
    rate_type = fields.Selection([
        ('daytime', 'Daytime (1.25x)'),
        ('nighttime', 'Nighttime (1.5x)'),
        ('rest_day', 'Weekly Rest Day (2.0x)'),
        ('public_holiday', 'Public Holiday (2.5x)')
    ], string='Overtime Type', default='daytime', required=True)
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved')], string='Status', default='draft')