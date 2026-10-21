from odoo import models, fields

class BelHrGrievanceCategory(models.Model):
    _name = 'bel.hr.grievance.category'
    _description = 'Grievance Complaint Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True, translate=True)
    description = fields.Text(string='Description')
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Default Severity', default='medium', required=True)
    responsible_team_id = fields.Many2one('res.groups', string='Default Responsible Group', help="Group responsible for managing cases in this category")
    expected_response_days = fields.Integer(string='Expected Response Time (Days)', default=3)
    expected_resolution_days = fields.Integer(string='Expected Resolution Time (Days)', default=14)
    confidentiality_level = fields.Selection([
        ('standard', 'Standard Confidential'),
        ('strict', 'Strictly Confidential'),
        ('anonymous_allowed', 'Anonymous Allowed')
    ], string='Confidentiality Classification', default='standard', required=True)
    active = fields.Boolean(string='Active', default=True)