from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

class BelHrGrievanceCase(models.Model):
    _name = 'bel.hr.grievance.case'
    _description = 'Employee Grievance Case'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Case Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    is_anonymous = fields.Boolean(string='Submit Anonymously', default=False, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Complainant', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    
    category_id = fields.Many2one('bel.hr.grievance.category', string='Category', required=True, tracking=True)
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Severity Level', compute='_compute_severity', store=True, readonly=False, tracking=True)
    
    incident_date = fields.Date(string='Incident Date', required=True, default=fields.Date.context_today)
    submission_date = fields.Date(string='Submission Date', readonly=True, default=fields.Date.context_today)
    response_deadline = fields.Date(string='Response Deadline', compute='_compute_deadlines', store=True)
    resolution_deadline = fields.Date(string='Resolution Deadline', compute='_compute_deadlines', store=True)

    description = fields.Html(string='Complaint Description', required=True)
    implicated_employee_ids = fields.Many2many('hr.employee', 'grievance_case_implicated_emp_rel', 'case_id', 'employee_id', string='Implicated Persons/Employees')
    implicated_department_id = fields.Many2one('hr.department', string='Implicated Department')

    stage_id = fields.Many2one('bel.hr.grievance.stage', string='Stage', tracking=True, copy=False,
                               default=lambda self: self.env['bel.hr.grievance.stage'].search([('stage_type', '=', 'draft')], limit=1))
    stage_type = fields.Selection(related='stage_id.stage_type', string='Stage Type', store=True)
    
    investigator_id = fields.Many2one('res.users', string='Assigned Investigator', tracking=True)
    reviewer_id = fields.Many2one('res.users', string='Designated Reviewer/Manager', tracking=True)
    
    investigation_ids = fields.One2many('bel.hr.grievance.investigation', 'case_id', string='Investigations')
    appeal_ids = fields.One2many('bel.hr.grievance.appeal', 'case_id', string='Appeals')

    # Resolution Fields
    findings = fields.Html(string='Investigation Findings')
    proposed_corrective_action = fields.Text(string='Proposed Corrective Action')
    resolution_outcome = fields.Selection([
        ('resolved', 'Resolved'),
        ('partially_resolved', 'Partially Resolved'),
        ('unsubstantiated', 'Unsubstantiated'),
        ('referred_disciplinary', 'Referred for Disciplinary Review'),
        ('further_investigation', 'Referred for Further Investigation')
    ], string='Resolution Outcome', tracking=True)
    resolution_date = fields.Date(string='Resolution Date', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('bel.hr.grievance.case') or _('New')
        return super(BelHrGrievanceCase, self).create(vals_list)

    @api.depends('category_id')
    def _compute_severity(self):
        for case in self:
            if case.category_id:
                case.severity = case.category_id.severity

    @api.depends('submission_date', 'category_id')
    def _compute_deadlines(self):
        for case in self:
            if case.submission_date and case.category_id:
                case.response_deadline = fields.Date.add(case.submission_date, days=case.category_id.expected_response_days)
                case.resolution_deadline = fields.Date.add(case.submission_date, days=case.category_id.expected_resolution_days)
            else:
                case.response_deadline = False
                case.resolution_deadline = False

    def action_submit(self):
        submitted_stage = self.env['bel.hr.grievance.stage'].search([('stage_type', '=', 'submitted')], limit=1)
        for case in self:
            if case.stage_type != 'draft':
                continue
            case.stage_id = submitted_stage or case.stage_id

    def action_assign_investigator(self):
        inv_stage = self.env['bel.hr.grievance.stage'].search([('stage_type', '=', 'investigation')], limit=1)
        for case in self:
            if not case.investigator_id:
                raise UserError(_("Please assign a responsible investigator before moving to Investigation stage."))
            case.stage_id = inv_stage or case.stage_id

    def action_propose_resolution(self):
        prop_stage = self.env['bel.hr.grievance.stage'].search([('stage_type', '=', 'proposed')], limit=1)
        for case in self:
            if not case.proposed_corrective_action or not case.resolution_outcome:
                raise UserError(_("Please provide proposed corrective action and resolution outcome before proposing resolution."))
            case.stage_id = prop_stage or case.stage_id

    def action_approve_resolution(self):
        app_stage = self.env['bel.hr.grievance.stage'].search([('stage_type', '=', 'approved')], limit=1)
        for case in self:
            case.stage_id = app_stage or case.stage_id
            case.resolution_date = fields.Date.context_today(self)

    def action_close(self):
        closed_stage = self.env['bel.hr.grievance.stage'].search([('stage_type', '=', 'closed')], limit=1)
        for case in self:
            case.stage_id = closed_stage or case.stage_id

    def action_escalate(self):
        esc_stage = self.env['bel.hr.grievance.stage'].search([('stage_type', '=', 'escalated')], limit=1)
        for case in self:
            case.stage_id = esc_stage or case.stage_id

    def action_dismiss(self):
        dism_stage = self.env['bel.hr.grievance.stage'].search([('stage_type', '=', 'dismissed')], limit=1)
        for case in self:
            case.stage_id = dism_stage or case.stage_id