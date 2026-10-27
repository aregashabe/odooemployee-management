from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    unpaid_leave_days = fields.Float(
        string='Unpaid Leave Days',
        compute='_compute_attendance_leave_adjustments',
        store=True,
        readonly=False
    )
    unpaid_leave_hours = fields.Float(
        string='Unpaid Leave Hours',
        compute='_compute_attendance_leave_adjustments',
        store=True,
        readonly=False
    )
    validated_worked_days = fields.Float(
        string='Validated Worked Days',
        compute='_compute_attendance_leave_adjustments',
        store=True,
        readonly=False
    )

    @api.depends('employee_id', 'date_from', 'date_to', 'contract_id')
    def _compute_attendance_leave_adjustments(self):
        for payslip in self:
            if not payslip.employee_id or not payslip.date_from or not payslip.date_to:
                payslip.unpaid_leave_days = 0.0
                payslip.unpaid_leave_hours = 0.0
                payslip.validated_worked_days = 0.0
                continue

            unpaid_days = 0.0

            # 1. Integration with bel_hr_leave_et
            if 'bel.hr.leave' in self.env:
                unpaid_leaves = self.env['bel.hr.leave'].search([
                    ('employee_id', '=', payslip.employee_id.id),
                    ('state', 'in', ['validate', 'approved', 'done']),
                    ('date_from', '>=', payslip.date_from),
                    ('date_to', '<=', payslip.date_to)
                ])
                for leave in unpaid_leaves:
                    if getattr(leave, 'is_unpaid', False):
                        unpaid_days += getattr(leave, 'number_of_days', 0.0)

            unpaid_hours = unpaid_days * 8.0

            # 2. Integration with bel_hr_attendance_rules
            worked_days = 26.0 - unpaid_days
            if 'bel.hr.attendance.rule' in self.env:
                attendances = self.env['bel.hr.attendance.rule'].search([
                    ('employee_id', '=', payslip.employee_id.id),
                    ('date', '>=', payslip.date_from),
                    ('date', '<=', payslip.date_to)
                ])
                if attendances:
                    total_worked_hours = sum(attendances.mapped('worked_hours'))
                    worked_days = total_worked_hours / 8.0 if total_worked_hours else worked_days

            payslip.unpaid_leave_days = unpaid_days
            payslip.unpaid_leave_hours = unpaid_hours
            payslip.validated_worked_days = worked_days

    def get_worked_day_lines(self, contracts, date_from, date_to):
        """Override standard worked day generator to insert Unpaid Leave deductions"""
        res = super(HrPayslip, self).get_worked_day_lines(contracts, date_from, date_to)
        
        for payslip in self:
            if payslip.unpaid_leave_days > 0:
                res.append({
                    'name': 'Unpaid Leave Deduction',
                    'code': 'UNPAID',
                    'number_of_days': payslip.unpaid_leave_days,
                    'number_of_hours': payslip.unpaid_leave_hours,
                    'contract_id': payslip.contract_id.id if payslip.contract_id else (contracts[0].id if contracts else False),
                })
        return res