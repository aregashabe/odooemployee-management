from odoo import models, fields

class HrOffboardingExitInterview(models.Model):
    _name = 'hr.offboarding.exit.interview'
    _description = 'Confidential Exit Interview Record'

    request_id = fields.Many2one('hr.offboarding.request', string='Offboarding Request', required=True, ondelete='cascade')
    interview_date = fields.Date(string='Interview Date', default=fields.Date.context_today)
    interviewer_id = fields.Many2one('res.users', string='Interviewer', default=lambda self: self.env.user)
    
    primary_reason = fields.Selection([
        ('better_offer', 'Better Compensation / Career Opportunity'),
        ('relocation', 'Relocation / Personal Reasons'),
        ('management', 'Dissatisfaction with Management'),
        ('work_environment', 'Work Environment / Culture'),
        ('retirement', 'Retirement'),
        ('other', 'Other'),
    ], string='Primary Reason for Leaving')

    feedback_positive = fields.Text(string='Positive Aspects / What went well')
    feedback_improvement = fields.Text(string='Areas of Improvement for Company')
    recommend_company = fields.Boolean(string='Would recommend company to others?', default=True)