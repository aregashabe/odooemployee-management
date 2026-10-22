from odoo import models, fields

class HrOffboardingClearance(models.Model):
    _name = 'hr.offboarding.clearance'
    _description = 'Departmental Offboarding Clearance'

    request_id = fields.Many2one('hr.offboarding.request', string='Offboarding Request', ondelete='cascade', required=True)
    department_name = fields.Char(string='Department / Section', required=True)
    responsible_user_id = fields.Many2one('res.users', string='Responsible Official', default=lambda self: self.env.user)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('cleared', 'Cleared'),
        ('rejected', 'Blocker / Issues Found'),
    ], string='Status', default='pending', required=True)
    
    completion_date = fields.Date(string='Cleared Date')
    notes = fields.Text(string='Clearance Remarks')

    def action_set_cleared(self):
        self.write({
            'status': 'cleared',
            'completion_date': fields.Date.context_today(self)
        })