# -*- coding: utf-8 -*-
{
    'name': 'Inventory Transfer Validation',

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "yousif basil almufti",
    'website': "https://www.yourcompany.com",

   
    'category': 'Inventory/Inventory',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','stock', 'fieldservice'],

    # always loaded
    'data': [
        #Security
        'security/groups.xml',
        'security/ir.model.access.csv',
        
        # Data
        # 'data/problem_data.xml',
        #wizard
        # 'wizard/inventory_transfer_wizard.xml',
        
        
        #Views
        'views/inventory_transfer_views.xml',
        
        
    ],
    
}

