from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta

class HrOffboardingRequest(models.Model):
    _name = 'hr.offboarding.request'
    _description = 'Employee Offboarding Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Reference', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', store=True, readonly=True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', store=True, readonly=True)
    manager_id = fields.Many2one('hr.employee', related='employee_id.parent_id', store=True, readonly=True)
    
    separation_type_id = fields.Many2one('hr.offboarding.type', string='Separation Type', required=True, tracking=True)
    request_date = fields.Date(string='Request Date', required=True, default=fields.Date.context_today, tracking=True)
    notice_period_days = fields.Integer(string='Notice Period (Days)', compute='_compute_notice_period', store=True, readonly=False)
    proposed_last_day = fields.Date(string='Proposed Last Working Day', compute='_compute_proposed_last_day', store=True, readonly=False)
    approved_last_day = fields.Date(string='Approved Last Working Day', tracking=True)
    
    reason = fields.Text(string='Separation Reason', required=True)
    hr_officer_id = fields.Many2one('res.users', string='Responsible HR Officer', default=lambda self: self.env.user, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('manager_approval', 'Manager Review'),
        ('hr_approval', 'HR Review'),
        ('clearance', 'Clearance Phase'),
        ('settlement', 'Final Settlement'),
        ('done', 'Completed'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
    ], string='Status', default='draft', tracking=True, index=True)

    clearance_ids = fields.One2many('hr.offboarding.clearance', 'request_id', string='Clearance Items')
    asset_ids = fields.One2many('hr.offboarding.asset', 'request_id', string='Assigned Assets')
    settlement_id = fields.Many2one('hr.offboarding.settlement', inverse_name='request_id', string='Final Settlement Record')
    exit_interview_id = fields.Many2one('hr.offboarding.exit.interview', inverse_name='request_id', string='Exit Interview')
    
    clearance_progress = fields.Float(string='Clearance Completion (%)', compute='_compute_clearance_progress')

    @api.depends('separation_type_id')
    def _compute_notice_period(self):
        for rec in self:
            if rec.separation_type_id:
                rec.notice_period_days = rec.separation_type_id.notice_period_days
            else:
                rec.notice_period_days = 30

    @api.depends('request_date', 'notice_period_days')
    def _compute_proposed_last_day(self):
        for rec in self:
            if rec.request_date:
                rec.proposed_last_day = rec.request_date + timedelta(days=rec.notice_period_days or 30)

    @api.depends('clearance_ids.status')
    def _compute_clearance_progress(self):
        for rec in self:
            total = len(rec.clearance_ids)
            if total > 0:
                completed = len(rec.clearance_ids.filtered(lambda c: c.status == 'cleared'))
                rec.clearance_progress = (completed / total) * 100
            else:
                rec.clearance_progress = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.offboarding.request') or _('New')
        return super().create(vals_list)

    def action_submit(self):
        self.write({'state': 'submitted'})
        self._generate_default_clearance_items()

    def action_manager_approve(self):
        self.write({'state': 'hr_approval'})

    def action_hr_approve(self):
        if not self.approved_last_day:
            self.approved_last_day = self.proposed_last_day
        self.write({'state': 'clearance'})

    def action_start_settlement(self):
        unresolved = self.clearance_ids.filtered(lambda c: c.status != 'cleared')
        if unresolved:
            raise ValidationError(_("Cannot proceed to settlement. All departmental clearance items must be set to 'Cleared'."))
        
        if not self.settlement_id:
            settlement = self.env['hr.offboarding.settlement'].create({
                'request_id': self.id,
                'employee_id': self.employee_id.id,
            })
            settlement.action_compute_settlement()
        self.write({'state': 'settlement'})

    def action_complete_offboarding(self):
        if not self.settlement_id or self.settlement_id.state != 'approved':
            raise UserError(_("Final Settlement must be approved before completing offboarding."))
        
        self.employee_id.write({
            'active': False,
            'departure_reason_id': False,
            'departure_description': f"Offboarding completed via {self.name}",
            'departure_date': self.approved_last_day or fields.Date.context_today(self),
        })
        self.write({'state': 'done'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_cancel(self):
        self.write({'state': 'canceled'})

    def _generate_default_clearance_items(self):
        departments = ['Human Resources', 'Finance & Payroll', 'IT & Infrastructure', 'Administration / Assets', 'Line Department']
        clearance_vals = []
        for dept in departments:
            clearance_vals.append({
                'request_id': self.id,
                'department_name': dept,
                'status': 'pending',
            })
        self.env['hr.offboarding.clearance'].create(clearance_vals)


