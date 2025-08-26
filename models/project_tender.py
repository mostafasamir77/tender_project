from odoo import fields,models,api
from odoo.exceptions import ValidationError

class ProjectTender(models.Model):
    _name = 'project.tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'project_name'

    job_order_ids = fields.One2many('job.order', 'project_tender_id' )

    project_id = fields.Many2one('project.project')
    analytic_account_id = fields.Many2one('account.analytic.account')

    status = fields.Selection([
        ('draft','Draft'),
        ('tendering','Tendering'),
        ('contracted','Contracted'),
        ('done','Done'),
        ('canceled','Canceled'),
    ], default='draft', tracking=True)

    project_name = fields.Char(required=True, tracking=True)
    customer_id = fields.Many2one('res.partner', tracking=True, required=True)
    create_date = fields.Date(readonly=True)
    accept_date = fields.Date(readonly=True, tracking=True)
    project_type = fields.Selection([
        ('direct_project','Direct Project'),
        ('tender','Tender'),
    ],default='tender' ,required=True ,tracking=True)
    start_date = fields.Date(tracking=True, required=True)
    responsible_user = fields.Many2one('res.users',tracking=True,required=True)
    location = fields.Char(tracking=True)



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


    def create_project(self):
        """ create the project and link it to the smart button """

        created_project_id = self.env['project.project'].create({
            'name' : self.project_name ,
            'partner_id' : self.customer_id.id ,
            'date_start' : self.start_date ,
            'account_id' : self.analytic_account_id.id ,
        })

        for rec in self:
            rec.project_id = created_project_id.id

    def create_analytic_account(self):
        created_analytic_account = self.env['account.analytic.account'].create({
            'name' : f"{self.project_name} Analytic" ,
            'partner_id' : self.customer_id.id ,
            'plan_id' : self.env['account.analytic.plan'].search([
                    ('name','=','Project') 
                ],limit=1 ).id ,
        })

        for rec in self:
            rec.analytic_account_id = created_analytic_account


    def import_action(self):
        """ open wizard to import the lines """

        action = self.env['ir.actions.actions']._for_xml_id('tender.import_button_wizard_action')
        action['context'] = {'default_project_tender_id' : self.id}
        return action


    def create_cost_sheet(self):
        """ Creates a cost sheet for each job order line and assigns the ID 
        of the created cost sheet to the corresponding Many2one field 
        in the job order """

        for line in self.job_order_ids:
            cost_sheet = self.env['cost.sheet'].create({
                'name' : line.product ,
                'project_id' : self.project_id.id ,
                'analytic_account_id' : self.analytic_account_id.id ,
                'job_order_id' : line.id ,
                'customer_id': self.customer_id.id ,
                'output_product': line.product ,
                'quantity' : line.quantity ,
                'UOM_id' : line.UOM_id.id ,
                'description' : line.description ,
            })
            # assign the cost sheet to the field that in the job order model 
            line.cost_sheet_id = cost_sheet.id


    def confirm_action(self):
        for rec in self:
            # change the statue to tendering
            rec.status = 'tendering'
            # assign value to accept date field
            rec.accept_date = fields.Date.today()
            # creating the analytic account
            self.create_analytic_account()
            # creating the project 
            self.create_project()
            # create cost sheet to each job order
            self.create_cost_sheet()

            
    def cancel_action(self):
        for rec in self:
            rec.status = 'canceled'



    def action_open_project(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'project',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

class JobOrder(models.Model):
    _name = 'job.order'

    project_tender_id = fields.Many2one('project.tender')

    product = fields.Char()
    description = fields.Char()
    quantity = fields.Float()
    UOM_id = fields.Many2one('uom.uom')
    cost_sheet_id = fields.Many2one('cost.sheet', readonly=True)

