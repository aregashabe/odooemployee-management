from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_bel_hr_payroll_et = fields.Boolean(string="Integrate Ethiopian Payroll")
    module_bel_hr_loan = fields.Boolean(string="Integrate Loan Adjustments")