from odoo import fields,models,api
from odoo.exceptions import ValidationError

class ProjectTender(models.Model):
    _name = 'project.tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'project_name'

    job_order_ids = fields.One2many('job.order', 'project_tender_id' )

    status = fields.Selection([
        ('draft','Draft'),
        ('tendering','Tendering'),
        ('contracted','Contracted'),
        ('done','Done'),
        ('canceled','Canceled'),
    ])

    project_name = fields.Char(required=True)
    customer_id = fields.Many2one('res.partner')
    create_date = fields.Date(readonly=True)
    accept_date = fields.Date(readonly=True)
    project_type = fields.Selection([
        ('direct_project','Direct Project'),
        ('tender','Tender'),
    ],default='tender' ,required=True)
    start_date = fields.Date()
    responsible_user = fields.Many2one('res.users')
    location = fields.Char()



    @api.constrains('project_name')
    def _check_unique_project_name(self):
        for record in self:
            if record.project_name:
                existing = self.search([
                    ('project_name', '=', record.project_name),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError('Project Name must be unique!')

    def import_lines_action(self):
        """ open the wizard that import the excel file """
        
        action = self.env['ir.actions.actions']._for_xml_id('tender.import_button_wizard_action')
        action['context'] = {'default_project_tender_id' : self.id}
        return action
    

    def confirm_action(self):
        pass     
    
    
    def cancel_action(self):
        for rec in self:
            rec.status = 'canceled'


class JobOrder(models.Model):
    _name = 'job.order'

    project_tender_id = fields.Many2one('project.tender')

    product = fields.Char()
    description = fields.Char()
    quantity = fields.Float()
    UOM_id = fields.Many2one('uom.uom')
    # cost_sheet = fields.Many2one('cost.sheet')

    # @api.model
    # def create(self, vals):
    #     import logging
    #     _logger = logging.getLogger(__name__)
        
    #     # Check if this is from the import button
    #     if self.env.context.get('open_wizzz'):
    #         _logger.info("Import action triggered!")
            
    #         # Call your import logic here
    #         # self.open_wizzz()
            
    #         # You can either:
    #         # 1. Return a wizard/action instead of creating a record
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Import Lines',
    #             'res_model': 'import.job.order.wizard',  # Your import wizard
    #             'view_mode': 'form',
    #             'target': 'new',
    #         }
            
    #         # OR 2. Create a record with default values after import
    #         # return super().create(vals)
        
    #     return super().create(vals)

    # def open_wizzz(self):
    #     import logging
    #     _logger = logging.getLogger(__name__)   
    #     _logger.info("ana tayh - Import method called")
        
    #     # Your import logic here
    #     pass