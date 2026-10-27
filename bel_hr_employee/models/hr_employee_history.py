from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployeeHistory(models.Model):
    _name = 'bel.hr.employee.history'
    _description = 'Employee Employment History'
    _order = 'effective_date desc, id desc'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='restrict',
        index=True,
    )

    
    change_type = fields.Selection(
        [
            ('salary', 'Salary Change'),
            ('job', 'Job Change'),
            ('department', 'Department Change'),
            ('grade', 'Grade Change'),
            ('contract', 'Contract Change'),
            ('allowance', 'Allowance Change'),
            ('benefits', 'Benefits Change'),
            ('working_schedule', 'Working Schedule Change'),
            ('probation', 'Probation Change'),
            ('pension', 'Pension Change'),
        ],
        string='Change Type',
        required=True,
        index=True,
    )


    effective_date = fields.Date(
        string='Effective Date',
        required=True,
        index=True,
    )

    previous_value = fields.Char(
        string='Previous Value',
        readonly=True,
    )

    new_value = fields.Char(
        string='New Value',
        required=True,
    )

    reason = fields.Text(
        string='Reason for Change',
        required=True,
    )

    approved_by = fields.Many2one(
        'res.users',
        string='Recorded By',
        readonly=True,
        required=True,
        default=lambda self: self.env.user,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['approved_by'] = self.env.user.id
        return super().create(vals_list)

    def write(self, vals):
        raise UserError(
            _("Historical records cannot be edited. Create a new record "
              "to document a correction or subsequent change.")
        )

    @api.ondelete(at_uninstall=False)
    def _prevent_history_deletion(self):
        raise UserError(
            _("Historical records cannot be deleted.")
        )