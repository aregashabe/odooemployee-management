from odoo import models, fields

class BelHrGrievanceInvestigation(models.Model):
    _name = 'bel.hr.grievance.investigation'
    _description = 'Grievance Case Investigation Entry'
    _order = 'activity_date desc'

    case_id = fields.Many2one('bel.hr.grievance.case', string='Grievance Case', required=True, ondelete='cascade')
    activity_date = fields.Datetime(string='Activity Date', default=fields.Datetime.now, required=True)
    investigator_id = fields.Many2one('res.users', string='Investigator', default=lambda self: self.env.user, required=True)
    activity_type = fields.Selection([
        ('statement', 'Witness / Party Statement'),
        ('evidence', 'Evidence Collection'),
        ('interview', 'Interview Conducted'),
        ('internal_note', 'Confidential Internal Note'),
        ('finding', 'Interim Finding')
    ], string='Activity Type', required=True, default='interview')
    
    summary = fields.Char(string='Summary', required=True)
    details = fields.Html(string='Detailed Notes')
    is_confidential = fields.Boolean(string='Strictly Confidential Note', default=True)