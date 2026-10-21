from odoo import models, fields, api, _

class BelHrGrievanceAppeal(models.Model):
    _name = 'bel.hr.grievance.appeal'
    _description = 'Grievance Case Appeal'
    _order = 'appeal_date desc'

    case_id = fields.Many2one('bel.hr.grievance.case', string='Grievance Case', required=True, ondelete='cascade')
    appeal_date = fields.Date(string='Appeal Date', default=fields.Date.context_today, required=True)
    appellant_id = fields.Many2one('hr.employee', string='Appellant Employee')
    reason = fields.Text(string='Reason for Appeal', required=True)
    
    independent_reviewer_id = fields.Many2one('res.users', string='Independent Reviewer', required=True)
    decision_date = fields.Date(string='Final Decision Date')
    appeal_findings = fields.Html(string='Appeal Review Findings')
    final_decision = fields.Selection([
        ('upheld', 'Original Resolution Upheld'),
        ('modified', 'Resolution Modified'),
        ('overturned', 'Original Decision Overturned'),
        ('reopened', 'Reopened for Re-investigation')
    ], string='Final Appeal Decision')
    
    state = fields.Selection([
        ('submitted', 'Appeal Submitted'),
        ('under_review', 'Under Independent Review'),
        ('decided', 'Decision Rendered')
    ], string='Appeal Status', default='submitted', required=True)

    def action_start_review(self):
        for appeal in self:
            appeal.state = 'under_review'

    def action_render_decision(self):
        for appeal in self:
            appeal.state = 'decided'
            appeal.decision_date = fields.Date.context_today(self)
            if appeal.final_decision == 'reopened':
                reopened_stage = self.env['bel.hr.grievance.stage'].search([('stage_type', '=', 'reopened')], limit=1)
                if reopened_stage:
                    appeal.case_id.stage_id = reopened_stage