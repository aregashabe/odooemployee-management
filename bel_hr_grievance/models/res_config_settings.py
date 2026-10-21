from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_bel_hr_disciplinary = fields.Boolean(
        string="Integrate with Disciplinary Management (bel_hr_disciplinary)"
    )
    grievance_allow_anonymous = fields.Boolean(
        string="Allow Anonymous Complaint Submissions",
        config_parameter='bel_hr_grievance.allow_anonymous',
        default=True
    )