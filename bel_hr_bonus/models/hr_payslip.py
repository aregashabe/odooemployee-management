from odoo import models

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        res = super().compute_sheet()
        for payslip in self:
            # Transfer approved bonus allocations for the employee and period into payroll inputs
            allocations = self.env['bel.bonus.allocation'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('state', '=', 'payroll_ready')
            ])
            for allocation in allocations:
                # Create or map to payroll input lines matching bel_hr_payroll_et requirements
                # Mark allocation as paid once computed/locked into payslip
                allocation.write({'state': 'paid'})
        return res