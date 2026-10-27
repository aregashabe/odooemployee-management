from odoo import models, fields, api, _

class HrOffboardingSettlement(models.Model):
    _name = 'hr.offboarding.settlement'
    _description = 'Ethiopian HRMS Final Settlement Engine'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Settlement Ref', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    request_id = fields.Many2one('hr.offboarding.request', string='Offboarding Request', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    basic_salary = fields.Monetary(string='Basic Monthly Salary', currency_field='currency_id')
    service_years = fields.Float(string='Total Years of Service', compute='_compute_service_duration', store=True)
    
    # Earnings
    unpaid_salary = fields.Monetary(string='Unpaid Basic Salary', currency_field='currency_id')
    leave_encashment_amount = fields.Monetary(string='Unused Leave Encashment', currency_field='currency_id')
    severance_amount = fields.Monetary(string='Ethiopian Statutory Severance', currency_field='currency_id')
    other_earnings = fields.Monetary(string='Other Approved Allowances/Earnings', currency_field='currency_id')
    total_gross = fields.Monetary(string='Total Gross Settlement', compute='_compute_totals', store=True)

    # Deductions
    income_tax_deduction = fields.Monetary(string='Employment Tax Deduction', currency_field='currency_id')
    pension_deduction = fields.Monetary(string='Pension Contribution Deduction', currency_field='currency_id')
    loan_deduction = fields.Monetary(string='Outstanding Loan Recovery', currency_field='currency_id')
    asset_deduction = fields.Monetary(string='Missing/Damaged Asset Deduction', currency_field='currency_id')
    other_deductions = fields.Monetary(string='Other Lawful Deductions', currency_field='currency_id')
    total_deductions = fields.Monetary(string='Total Deductions', compute='_compute_totals', store=True)

    # Net
    net_settlement = fields.Monetary(string='Net Settlement Payable', compute='_compute_totals', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('approved', 'Approved & Locked'),
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.offboarding.settlement') or _('New')
        return super().create(vals_list)

    
    @api.depends(
        'employee_id.original_joining_date',
        'employee_id.ethiopian_employment_start_date',
        'request_id.approved_last_day',
    )
    def _compute_service_duration(self):
        for rec in self:
            employee = rec.employee_id
            start_date = (
                employee.original_joining_date
                or employee.ethiopian_employment_start_date
            )

            if employee and start_date:
                end_date = (
                    rec.request_id.approved_last_day
                    or fields.Date.context_today(rec)
                )
                delta_days = (end_date - start_date).days
                rec.service_years = round(
                    max(delta_days, 0) / 365.25, 2
                )
            else:
                rec.service_years = 0.0


    @api.depends('unpaid_salary', 'leave_encashment_amount', 'severance_amount', 'other_earnings',
                 'income_tax_deduction', 'pension_deduction', 'loan_deduction', 'asset_deduction', 'other_deductions')
    def _compute_totals(self):
        for rec in self:
            rec.total_gross = rec.unpaid_salary + rec.leave_encashment_amount + rec.severance_amount + rec.other_earnings
            rec.total_deductions = rec.income_tax_deduction + rec.pension_deduction + rec.loan_deduction + rec.asset_deduction + rec.other_deductions
            rec.net_settlement = rec.total_gross - rec.total_deductions

    def action_compute_settlement(self):
        for rec in self:
            rec.basic_salary = rec.employee_id.contract_id.wage if hasattr(rec.employee_id, 'contract_id') and rec.employee_id.contract_id else 0.0
            
            # Ethiopian Labor Proclamation Severance Rules
            if rec.request_id.separation_type_id.requires_severance and rec.service_years >= 1.0:
                first_year_severance = rec.basic_salary
                additional_years = rec.service_years - 1.0
                additional_severance = (additional_years * (rec.basic_salary / 3.0))
                rec.severance_amount = round(first_year_severance + additional_severance, 2)
            else:
                rec.severance_amount = 0.0

            asset_deductions = sum(rec.request_id.asset_ids.mapped('financial_deduction'))
            rec.asset_deduction = asset_deductions

            if 'hr.loan' in self.env:
                loans = self.env['hr.loan'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', '=', 'approve')
                ])
                rec.loan_deduction = sum(loans.mapped('balance_amount')) if hasattr(loans, 'balance_amount') else 0.0

            rec.state = 'calculated'

    def action_approve_settlement(self):
        self.write({'state': 'approved'})