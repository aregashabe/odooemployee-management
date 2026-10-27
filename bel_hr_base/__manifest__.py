{
    'name': 'BelTech HR Base',
    'version': '19.0.1.0.0',
    'summary': 'Company-specific HR policies and configuration',
    'category': 'Human Resources',
    'author': 'BelTech',
    'license': 'LGPL-3',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/hr_policy_views.xml',
    ],
    'installable': True,
    'application': False,
}
