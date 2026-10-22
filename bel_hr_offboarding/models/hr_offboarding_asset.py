from odoo import models, fields

class HrOffboardingAsset(models.Model):
    _name = 'hr.offboarding.asset'
    _description = 'Offboarding Asset Return Tracking'

    request_id = fields.Many2one('hr.offboarding.request', string='Offboarding Request', ondelete='cascade', required=True)
    asset_name = fields.Char(string='Asset Name / Identification', required=True)
    serial_number = fields.Char(string='Serial Number')
    assigned_date = fields.Date(string='Assigned Date')
    condition = fields.Selection([
        ('good', 'Good / Working'),
        ('damaged', 'Damaged'),
        ('missing', 'Missing / Unreturned'),
    ], string='Returned Condition', default='good')
    
    is_returned = fields.Boolean(string='Returned', default=False)
    financial_deduction = fields.Float(string='Authorized Deduction Amount', default=0.0)
    notes = fields.Text(string='Handover Notes')