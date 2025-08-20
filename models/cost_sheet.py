from odoo import fields, models, api

class CostSheet(models.Model):
    _name = 'cost.sheet'
    _rec_name =  'ref'

    material_ids = fields.One2many('material.material', 'cost_sheet_id')
    equipment_ids = fields.One2many('equipment.equipment', 'cost_sheet_id')
    labor_ids = fields.One2many('labor.labor', 'cost_sheet_id', string='labor')

    ref = fields.Char(readonly=True, default='New')
    name = fields.Char()
    project_id = fields.Many2one('project.project')
    analytic_account_id = fields.Many2one('account.analytic.account')
    job_order_id = fields.Many2one('job.order')
    customer_id = fields.Many2one('res.partner')
    expected_start_date = fields.Date()
    expected_end_date = fields.Date()
    BOQ_expected_duration_per_days = fields.Date(compute='_compute_BOQ_expected_duration_per_days')
    output_product = fields.Char()
    quantity = fields.Float()
    UOM_id = fields.Many2one('uom.uom')
    create_date = fields.Date(readonly=True)
    close_date = fields.Date()
    create_uid = fields.Many2one('res.users', string='Created By')
    description = fields.Char()
    additional_expenses_type = fields.Selection([
        ('percentage','Percentage'),
        ('fixed_amount','Fixed Amount'),
    ],string='Additional Expenses', default='percentage',required=True)
    additional_expenses_value = fields.Float()
    risk = fields.Float(string='Risk %')
    margin = fields.Float(string='Margin %')



    @api.model
    def create(self,vals):
        res = super(CostSheet,self).create(vals)
        if res.ref == 'New' :
            res.ref = self.env['ir.sequence'].next_by_code('cost_sheet_seq')
        return res    

    @api.depends('expected_end_date')
    def _compute_BOQ_expected_duration_per_days(self):
        for rec in self:
            rec.BOQ_expected_duration_per_days = rec.expected_start_date - rec.expected_end_date



class Material(models.Model):
    _name = 'material.material'
    cost_sheet_id = fields.Many2one('cost.sheet')

    job_type = fields.Selection([
        ('material','Material'),
        ('equipment','Equipment'),
        ('labor','Labor'),
        ('over_head','Over Head'),
    ], default='material' , required=True , readonly=True)
    product_id = fields.Many2one('product.template')
    description = fields.Char()
    factor = fields.Float()
    planned_quantity = fields.Float(compute='_compute_planned_quantity')
    wastage = fields.Float(string="Wastage %")
    quantity_after_wastage = fields.Float(compute='_compute_quantity_after_wastage')
    cost_per_uom = fields.Float(related='product_id.standard_price')
    cost_price_sub_total = fields.Float(compute='_compute_cost_price_sub_total')

    @api.depends('factor')
    def _compute_planned_quantity(self):
        for rec in self:
            rec.planned_quantity = rec.factor * rec.cost_sheet_id.quantity 
            
    @api.depends('planned_quantity', 'wastage')
    def _compute_quantity_after_wastage (self):
        for rec in self:
            rec.quantity_after_wastage  = rec.planned_quantity * (rec.wastage/100) + rec.planned_quantity

    @api.depends('quantity_after_wastage', 'cost_per_uom')
    def _compute_cost_price_sub_total(self):
        for rec in self: 
            rec.cost_price_sub_total = rec.quantity_after_wastage * rec.cost_per_uom




class Equipment(models.Model):
    _name = 'equipment.equipment'

    cost_sheet_id = fields.Many2one('cost.sheet')

    job_type = fields.Selection([
        ('material','Material'),
        ('equipment','Equipment'),
        ('labor','Labor'),
        ('over_head','Over Head'),
    ], default='equipment' , required=True , readonly=True)

    equipment_id = fields.Many2one('maintenance.equipment')
    no_of_required_equipment = fields.Float()
    total_working_hours = fields.Float()
    cost_per_hour = fields.Float()
    sub_total = fields.Float(compute='_compute_sub_total')

    @api.depends('total_working_hours', 'cost_per_hour')
    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.no_of_required_equipment * rec.total_working_hours * rec.cost_per_hour

class Labor(models.Model):
    _name = 'labor.labor'

    cost_sheet_id = fields.Many2one('cost.sheet')

    job_type = fields.Selection([
        ('material','Material'),
        ('equipment','Equipment'),
        ('labor','Labor'),
        ('over_head','Over Head'),
    ], default='labor' , required=True , readonly=True)
    job_position_id = fields.Many2one('hr.job')
    description = fields.Char()
    no_of_manpower = fields.Integer()
    total_working_hours = fields.Float()
    cost_per_hour = fields.Float()
    sub_total = fields.Float(compute='_compute_sub_total')

    def _compute_sub_total(self):
        for rec in self :
            rec.sub_total = rec.no_of_manpower * rec.total_working_hours * rec.cost_per_hour 





