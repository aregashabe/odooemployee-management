
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bel_hr_default_probation_months = fields.Integer(
        string='Default Probation Period (Months)',
        related='company_id.bel_hr_default_probation_months',
        readonly=False,
    )

    bel_hr_contract_reminder_days = fields.Integer(
        string='Contract Expiration Reminder (Days)',
        related='company_id.bel_hr_contract_reminder_days',
        readonly=False,
    )

    bel_hr_require_contract_approval = fields.Boolean(
        string='Require Contract Approval',
        related='company_id.bel_hr_require_contract_approval',
        readonly=False,
    )
