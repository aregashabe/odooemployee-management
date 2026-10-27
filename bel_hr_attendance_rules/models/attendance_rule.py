from odoo import models, fields

class BelHrAttendanceRule(models.Model):
    _name = 'bel.hr.attendance.rule'
    _description = 'BelTech Attendance Rules'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Date(string='Attendance Date', required=True, default=fields.Date.context_today)
    worked_hours = fields.Float(string='Worked Hours', default=8.0)
    state = fields.Selection([('normal', 'Normal'), ('late', 'Late'), ('absent', 'Absent')], string='Status', default='normal')