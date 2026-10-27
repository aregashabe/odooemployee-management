from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BelBonusAllocation(models.Model):
    _name = 'bel.bonus.allocation'
    _description = 'Employee Bonus Allocation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Allocation Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', store=True, string='Department')
    company_id = fields.Many2one('res.company', related='employee_id.company_id', store=True, string='Company')
    
    bonus_type_id = fields.Many2one('bel.bonus.type', string='Bonus Type', required=True, tracking=True)
    policy_id = fields.Many2one('bel.bonus.policy', string='Bonus Policy', tracking=True)
    bonus_period = fields.Char(string='Bonus Period (e.g., 2026)', required=True, tracking=True)
    
    calculation_method = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Salary'),
        ('performance', 'Performance-Based'),
        ('target', 'Target-Based'),
        ('manual', 'Manual Bonus'),
    ], string='Calculation Method', required=True, default='fixed', tracking=True)
    
    calculated_amount = fields.Float(string='Calculated Amount', tracking=True)
    approved_amount = fields.Float(string='Approved Amount', tracking=True)
    reason = fields.Text(string='Reason / Justification')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('manager_approved', 'Manager Approved'),
        ('hr_approved', 'HR Approved'),
        ('finance_approved', 'Finance Approved'),
        ('payroll_ready', 'Payroll Ready'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('bel.bonus.allocation') or 'New'
        return super().create(vals_list)

    @api.onchange('policy_id', 'employee_id')
    def _onchange_policy_id(self):
        """ Automatically populate calculation method and compute amount based on policy """
        for rec in self:
            if rec.policy_id:
                rec.calculation_method = rec.policy_id.calculation_method
                if rec.calculation_method == 'fixed':
                    rec.calculated_amount = rec.policy_id.fixed_amount
                    rec.approved_amount = rec.policy_id.fixed_amount
                elif rec.calculation_method == 'percentage' and rec.employee_id:
                    contract = self.env['hr.contract'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('state', 'in', ['open', 'running'])
                    ], limit=1)
                    if contract:
                        wage = contract.wage
                        rate = rec.policy_id.percentage_rate or 0.0
                        calc = wage * (rate / 100.0)
                        if rec.policy_id.max_bonus_limit and calc > rec.policy_id.max_bonus_limit:
                            calc = rec.policy_id.max_bonus_limit
                        rec.calculated_amount = calc
                        rec.approved_amount = calc

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_manager_approve(self):
        self.write({'state': 'manager_approved'})

    def action_hr_approve(self):
        self.write({'state': 'hr_approved'})

    def action_finance_approve(self):
        self.write({'state': 'finance_approved'})

    def action_mark_payroll_ready(self):
        self.write({'state': 'payroll_ready'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'paid':
                raise ValidationError("Cannot cancel a bonus allocation that has already been paid via payroll.")
            rec.write({'state': 'cancelled'})