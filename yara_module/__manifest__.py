
{
    'name': 'Yara module',
    'version': '1.0',
    'category': '',
    'license': 'AGPL-3',
    'summary': '',
    'description': """
    Delivery status from nshift
    """,
    'author': "Yara",
    'website': '',
    'depends': ['sale', 'stock', 'delivery'],
    'data': [
        'data/updatestatus.xml',
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/sale_views.xml',             
    ],
    'installable': True,
}