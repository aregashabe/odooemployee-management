
{
    'name': 'BelTech Ethiopian HR Employee',
    'version': '19.0.1.0.0',
    'summary': 'Ethiopian employee information and HR management',
    'description': """
        BelTech Ethiopian HRMS V1

        Extends standard Odoo employee management with:
        - Ethiopian employee information
        - Employment categories and probation
        - Compensation and employment history
        - Company-specific HR policies
    """,
    'category': 'Human Resources',
    'author': 'BelTech',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'bel_hr_base',
        'hr_holidays',
    ],
    
'data': [
    'security/ir.model.access.csv',
    'security/security.xml',
    'views/hr_employee_views.xml',
    'views/hr_employee_contract_views.xml',
    'views/hr_employee_history_views.xml',
    'data/contract_reminder.xml',
    'views/hr_employee_lifecycle_views.xml',
],

    'installable': True,
    'application': False,
}
