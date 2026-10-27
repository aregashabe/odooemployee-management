from odoo import api, fields, models, _
from odoo.exceptions import UserError

# Users who may READ the suspension fields.
# HR Officers need this to open the employee form at all.
# WRITE is still blocked in the action methods below.
HR_READ_GROUPS = "hr.group_hr_user,hr.group_hr_manager"


class HrEmployeeLifecycle(models.Model):
    _inherit = "hr.employee"

    bel_lifecycle_status = fields.Selection(
        [
            ("new", "New / Draft"),
            ("active", "Active"),
            ("probation", "On Probation"),
            ("leave", "On Leave"),
            ("suspended", "Suspended"),
            ("departed", "Terminated / Resigned"),
            ("archived", "Archived"),
        ],
        string="Employment Status",
        compute="_compute_bel_lifecycle_status",
    )

    bel_suspension_start_date = fields.Date(
        string="Suspension Start Date",
        groups=HR_READ_GROUPS,
        copy=False,
    )

    bel_suspension_end_date = fields.Date(
        string="Suspension End Date",
        groups=HR_READ_GROUPS,
        copy=False,
    )

    bel_suspension_reason = fields.Text(
        string="Suspension Reason",
        groups=HR_READ_GROUPS,
        copy=False,
    )

    bel_suspended_by = fields.Many2one(
        "res.users",
        string="Suspended By",
        readonly=True,
        groups=HR_READ_GROUPS,
        copy=False,
    )

    bel_suspension_recorded_on = fields.Datetime(
        string="Suspension Recorded On",
        readonly=True,
        groups=HR_READ_GROUPS,
        copy=False,
    )

    @api.depends(
        "active",
        "departure_date",
        "departure_reason_id",
        "ethiopian_employment_start_date",
        "probation_start_date",
        "probation_end_date",
        "trial_date_end",
        "current_version_id",
        "current_version_id.date_start",
        "current_version_id.trial_date_end",
        "is_absent",
        "bel_suspension_start_date",
        "bel_suspension_end_date",
    )
    def _compute_bel_lifecycle_status(self):
        today = fields.Date.context_today(self)

        # Compute in sudo() so we can read Manager-only core fields
        # such as trial_date_end / current_version_id.trial_date_end.
        # The computed result is written back to the plain
        # bel_lifecycle_status field, which has no group restriction,
        # so no access rule is bypassed for the user.
        for employee, emp_sudo in zip(self, self.sudo()):
            status = "new"

            version = emp_sudo.current_version_id

            employment_start = (
                emp_sudo.ethiopian_employment_start_date
                or (version.date_start if version else False)
            )

            probation_start = (
                emp_sudo.probation_start_date
                or employment_start
            )

            probation_end = (
                emp_sudo.probation_end_date
                or emp_sudo.trial_date_end
                or (version.trial_date_end if version else False)
            )

            # A completed departure takes precedence over archiving.
            if (
                emp_sudo.departure_date
                and emp_sudo.departure_date <= today
            ):
                status = "departed"

            elif not emp_sudo.active:
                status = "archived"

            elif (
                emp_sudo.bel_suspension_start_date
                and emp_sudo.bel_suspension_start_date <= today
                and (
                    not emp_sudo.bel_suspension_end_date
                    or emp_sudo.bel_suspension_end_date >= today
                )
            ):
                status = "suspended"

            elif emp_sudo.is_absent:
                status = "leave"

            elif (
                probation_start
                and probation_end
                and probation_start <= today <= probation_end
            ):
                status = "probation"

            elif employment_start and employment_start <= today:
                status = "active"

            employee.bel_lifecycle_status = status

    def action_bel_suspend_employee(self):
        self.ensure_one()

        if not self.env.user.has_group("hr.group_hr_manager"):
            raise UserError(
                _("Only an HR Manager can suspend an employee.")
            )

        if not self.bel_suspension_reason:
            raise UserError(
                _("Enter the suspension reason before suspending.")
            )

        today = fields.Date.context_today(self)

        self.write({
            "bel_suspension_start_date": today,
            "bel_suspension_end_date": False,
            "bel_suspended_by": self.env.user.id,
            "bel_suspension_recorded_on": fields.Datetime.now(),
        })

        return True

    def action_bel_end_suspension(self):
        self.ensure_one()

        if not self.env.user.has_group("hr.group_hr_manager"):
            raise UserError(
                _("Only an HR Manager can end a suspension.")
            )

        if not self.bel_suspension_start_date:
            raise UserError(
                _("There is no suspension record to end.")
            )

        today = fields.Date.context_today(self)

        if self.bel_suspension_start_date > today:
            raise UserError(
                _("The suspension has not started yet.")
            )

        self.write({
            "bel_suspension_end_date": today,
        })

        return True