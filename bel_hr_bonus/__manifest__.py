{
    'name': 'BelTech Ethiopian HRMS Bonus & Incentive Management',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Configurable Employee Bonus, Incentive Management, and Ethiopian Payroll Integration',
    'author': 'BelTech',
    'depends': [
        'hr',
        'bel_hr_base',
        'bel_hr_employee',
    # Updated from bel_hr_appraisal to standard Odoo hr_appraisal
        'bel_hr_payroll_et',
    ],
    'data': [
        'security/bonus_security.xml',
        'security/ir.model.access.csv',
        'data/bonus_type_data.xml',
        'data/salary_rule_bonus_data.xml',
        'data/bonus_sequence.xml',
        'views/bonus_type_views.xml',
        'views/bonus_policy_views.xml',
        'views/bonus_allocation_views.xml',
        'views/bonus_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}