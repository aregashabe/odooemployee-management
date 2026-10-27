{
    'name': 'BelTech Ethiopian HRMS - Offboarding & Final Settlement',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Employees',
    'summary': 'Manage employee separations, clearances, Ethiopian severance, and final settlements in Odoo 19.',
    'description': """
BelTech Ethiopian HRMS Offboarding & Final Settlement Module
=============================================================
* Configurable Separation Types & Notice Periods
* Multi-departmental Clearance Tracking
* Company Asset Return Verification
* Integration with Ethiopian Payroll, Time Off, and Loans
* Ethiopian Labor Proclamation Severance & Statutory Entitlements
* QWeb Final Settlement Statement & Exit Certification
    """,
    'author': 'BelTech',
    'website': 'https://www.beltech.et',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'mail',
        'hr_holidays',
        'bel_hr_base',
        'bel_hr_employee',
    ],
    'data': [
        'security/offboarding_security.xml',
        'security/ir.model.access.csv',
        'data/offboarding_type_data.xml',
        'views/hr_offboarding_type_views.xml',
        'views/hr_offboarding_request_views.xml',
        'views/hr_offboarding_clearance_views.xml',
        'views/hr_offboarding_settlement_views.xml',
        'views/hr_offboarding_exit_interview_views.xml',
        'views/menu_views.xml',
        'report/offboarding_reports.xml',
        'report/report_final_settlement.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}