
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    bel_hr_default_probation_months = fields.Integer(
        string='Default Probation Period (Months)',
        default=3,
    )

    bel_hr_contract_reminder_days = fields.Integer(
        string='Contract Expiration Reminder (Days)',
        default=30,
    )

    bel_hr_require_contract_approval = fields.Boolean(
        string='Require Contract Approval',
        default=True,
        help=(
            'When enabled, employment contracts must be submitted '
            'and approved by an HR manager before they are considered approved.'
        ),
    )
