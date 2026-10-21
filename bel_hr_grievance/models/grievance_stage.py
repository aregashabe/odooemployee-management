from odoo import models, fields

class BelHrGrievanceStage(models.Model):
    _name = 'bel.hr.grievance.stage'
    _description = 'Grievance Case Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    stage_type = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('review', 'Under Review'),
        ('investigation', 'Investigation'),
        ('proposed', 'Resolution Proposed'),
        ('approved', 'Approved'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
        ('dismissed', 'Dismissed / Rejected'),
        ('appeal', 'Under Appeal'),
        ('reopened', 'Reopened')
    ], string='Stage Type', default='draft', required=True)
    is_closed = fields.Boolean(string='Is Closed Stage', default=False)
    fold = fields.Boolean(string='Folded in Kanban', default=False)