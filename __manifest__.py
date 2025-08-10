{
    'name': "Tender",
    'author': "Mostafa Samir",
    'version': '18.1',
    'depends': ['base', 'contacts', 'mail', 'stock', 'project', 'accountant','maintenance','hr'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/sequence.xml',
        'views/base.xml',
        'views/project_tender_view.xml',
        'wizard/project_tender_wizard_view.xml',
    ],
    'assets': {
        'web.assets_backend' : ['tender/static/src/css/tender.css']
    },
    'application': True,
}