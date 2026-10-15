
from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError
class HrVersionContract(models.Model):
    _inherit = "hr.version"
    
    bel_approval_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("not_required", "Approval Not Required"),
        ],
        string="Approval Status",
        default="draft",
        required=True,
        copy=False,
        index=True,
    )

    bel_submitted_by = fields.Many2one(
        "res.users",
        string="Submitted By",
        readonly=True,
        copy=False,
    )
    bel_submitted_on = fields.Datetime(
        string="Submitted On",
        readonly=True,
        copy=False,
    )
    bel_approved_by = fields.Many2one(
        "res.users",
        string="Decision By",
        readonly=True,
        copy=False,
    )
    bel_approved_on = fields.Datetime(
        string="Decision On",
        readonly=True,
        copy=False,
    )
    bel_rejection_reason = fields.Text(
        string="Rejection Reason",
        copy=False,
    )


    bel_allowance_amount = fields.Monetary(
        string="Total Allowances",
        currency_field="currency_id",
        default=0.0,
        groups="hr.group_hr_user",
    )

    bel_allowance_details = fields.Text(
        string="Allowance Details",
        groups="hr.group_hr_user",
    )

    bel_benefits = fields.Text(
        string="Benefits",
        groups="hr.group_hr_user",
    )

    bel_compensation_terms = fields.Text(
        string="Compensation Terms",
        groups="hr.group_hr_user",
    )

    bel_renewal_of_id = fields.Many2one(
        "hr.version",
        string="Renewed From",
        readonly=True,
        copy=False,
        ondelete="set null",
    )

    _BEL_HISTORY_FIELDS = {
        "contract_date_start": "contract",
        "contract_date_end": "contract",
        "contract_type_id": "contract",
        "bel_contract_reference": "contract",
        "wage": "salary",
        "bel_allowance_amount": "allowance",
        "bel_allowance_details": "allowance",
        "bel_benefits": "benefits",
        "bel_compensation_terms": "benefits",
        "resource_calendar_id": "working_schedule",
        "bel_probation_start_date": "probation",
        "trial_date_end": "probation",
        "bel_pension_eligible": "pension",
        "bel_pension_scheme": "pension",
    }

    def _bel_history_display_value(self, field_name):
        self.ensure_one()

        value = self[field_name]
        field = self._fields[field_name]

        if field.type == "many2one":
            return value.display_name if value else "Not set"

        if field.type == "boolean":
            return "Yes" if value else "No"

        if field.type == "selection":
            selection = field.selection
            if isinstance(selection, list):
                return dict(selection).get(value, value or "Not set")

        return str(value) if value not in (False, None, "") else "Not set"

    def _bel_record_history(
        self, change_type, previous_value, new_value, reason
    ):
        self.ensure_one()

        if not self.employee_id:
            return

        self.env["bel.hr.employee.history"].create({
            "employee_id": self.employee_id.id,
            "change_type": change_type,
            "effective_date": (
                self.contract_date_start
                or self.date_version
                or fields.Date.context_today(self)
            ),
            "previous_value": previous_value,
            "new_value": new_value,
            "reason": reason,
        })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        for record in records:
            if record.employee_id:
                details = (
                    f"Reference: {record.bel_contract_reference or 'Not set'}; "
                    f"start: {record.contract_date_start or 'Not set'}; "
                    f"end: {record.contract_date_end or 'Not set'}"
                )
                record._bel_record_history(
                    "contract",
                    "No previous contract record",
                    details,
                    "Initial contract/version record created.",
                )

        return records

    def write(self, vals):
        
        approval_fields = {
            "bel_approval_state",
            "bel_submitted_by",
            "bel_submitted_on",
            "bel_approved_by",
            "bel_approved_on",
        }

        if (
            approval_fields.intersection(vals)
            and not self.env.context.get("bel_approval_action")
        ):
            raise AccessError(
                "Approval status and audit fields must be changed "
                "through the contract approval actions."
            )

        if (
            "bel_rejection_reason" in vals
            and not self.env.context.get("bel_approval_action")
            and not self.env.user.has_group("hr.group_hr_manager")
        ):
            raise AccessError(
                "Only an HR manager can enter or change a rejection reason."
            )

        tracked_fields = [
            name
            for name in self._BEL_HISTORY_FIELDS
            if name in vals
        ]

        old_values = {
            record.id: {
                name: record._bel_history_display_value(name)
                for name in tracked_fields
            }
            for record in self
        }

        result = super().write(vals)

        for record in self:
            for name in tracked_fields:
                previous = old_values[record.id][name]
                current = record._bel_history_display_value(name)

                if previous == current:
                    continue

                record._bel_record_history(
                    self._BEL_HISTORY_FIELDS[name],
                    previous,
                    current,
                    f"Automatically recorded change to {record._fields[name].string}.",
                )

        return result
    
    
    def _bel_check_hr_user(self):
        if not (
            self.env.user.has_group("hr.group_hr_user")
            or self.env.user.has_group("hr.group_hr_manager")
        ):
            raise AccessError(
                "Only HR officers or HR managers can manage contract approval."
            )

    def _bel_check_hr_manager(self):
        if not self.env.user.has_group("hr.group_hr_manager"):
            raise AccessError(
                "Only an HR manager can approve or reject an employment contract."
            )

    def action_bel_submit_for_approval(self):
        self._bel_check_hr_user()

        for record in self:
            if not record.employee_id:
                raise UserError(
                    "An employee must be assigned before submitting the contract."
                )

            if record.bel_approval_state not in ("draft", "rejected"):
                raise UserError(
                    "Only draft or rejected contracts can be submitted."
                )

            company = record.employee_id.company_id
            requires_approval = company.bel_hr_require_contract_approval

            values = {
                "bel_approval_state": (
                    "pending" if requires_approval else "not_required"
                ),
                "bel_submitted_by": self.env.user.id,
                "bel_submitted_on": fields.Datetime.now(),
                "bel_approved_by": False,
                "bel_approved_on": False,
                "bel_rejection_reason": False,
            }

            record.with_context(bel_approval_action=True).write(values)

    def action_bel_approve_contract(self):
        self._bel_check_hr_manager()

        for record in self:
            if record.bel_approval_state != "pending":
                raise UserError(
                    "Only contracts pending approval can be approved."
                )

            record.with_context(bel_approval_action=True).write({
                "bel_approval_state": "approved",
                "bel_approved_by": self.env.user.id,
                "bel_approved_on": fields.Datetime.now(),
                "bel_rejection_reason": False,
            })

    def action_bel_reject_contract(self):
        self._bel_check_hr_manager()

        for record in self:
            if record.bel_approval_state != "pending":
                raise UserError(
                    "Only contracts pending approval can be rejected."
                )

            if not (record.bel_rejection_reason or "").strip():
                raise UserError(
                    "Enter a rejection reason before rejecting the contract."
                )

            record.with_context(bel_approval_action=True).write({
                "bel_approval_state": "rejected",
                "bel_approved_by": self.env.user.id,
                "bel_approved_on": fields.Datetime.now(),
            })

    def action_bel_prepare_renewal(self):
        self.ensure_one()

        start_date = fields.Date.context_today(self)
        if self.contract_date_end:
            start_date = self.contract_date_end + timedelta(days=1)

        return {
            "type": "ir.actions.act_window",
            "name": "Renew Employment Contract",
            "res_model": "hr.version",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_employee_id": self.employee_id.id,
                "default_date_version": start_date,
                "default_contract_date_start": start_date,
                "default_contract_type_id": self.contract_type_id.id,
                "default_wage": self.wage,
                "default_contract_wage": self.contract_wage,
                "default_resource_calendar_id": (
                    self.resource_calendar_id.id
                ),
                "default_bel_employment_category_id": (
                    self.bel_employment_category_id.id
                ),
                "default_bel_allowance_amount": self.bel_allowance_amount,
                "default_bel_allowance_details": self.bel_allowance_details,
                "default_bel_benefits": self.bel_benefits,
                "default_bel_compensation_terms": (
                    self.bel_compensation_terms
                ),
                "default_bel_pension_eligible": self.bel_pension_eligible,
                "default_bel_pension_scheme": self.bel_pension_scheme,
                "default_bel_renewal_of_id": self.id,
            },
        }

    @api.model
    def _cron_bel_contract_expiry_reminder(self):
        today = fields.Date.context_today(self)
        reminder_date = today + timedelta(days=30)

        activity_type = self.env.ref(
            "mail.mail_activity_data_todo",
            raise_if_not_found=False,
        )
        if not activity_type:
            return

        versions = self.search([
            ("contract_date_end", ">=", today),
            ("contract_date_end", "<=", reminder_date),
            ("employee_id", "!=", False),
        ])

        for version in versions:
            summary = "Employment contract expiration"

            existing = version.activity_ids.filtered(
                lambda activity:
                    activity.activity_type_id == activity_type
                    and activity.summary == summary
            )
            if existing:
                continue

            user = version.employee_id.user_id or self.env.user

            version.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=version.contract_date_end,
                summary=summary,
                note=(
                    "Review the employment contract for "
                    f"{version.employee_id.display_name}. "
                    f"Contract end date: {version.contract_date_end}. "
                    "Review renewal or separation requirements."
                ),
                user_id=user.id,
            )
