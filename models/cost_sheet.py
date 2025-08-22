from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class CostSheet(models.Model):
    _name = 'cost.sheet'
    _rec_name =  'ref'

    material_ids = fields.One2many('material.material', 'cost_sheet_id')
    equipment_ids = fields.One2many('equipment.equipment', 'cost_sheet_id')
    labor_ids = fields.One2many('labor.labor', 'cost_sheet_id', string='labor')
    over_head_ids = fields.One2many('over.head', 'cost_sheet_id')

    ref = fields.Char(readonly=True, default='New')
    name = fields.Char()
    project_id = fields.Many2one('project.project')
    analytic_account_id = fields.Many2one('account.analytic.account')
    job_order_id = fields.Many2one('job.order')
    customer_id = fields.Many2one('res.partner')
    expected_start_date = fields.Date()
    expected_end_date = fields.Date()
    BOQ_expected_duration_per_days = fields.Integer(compute='_compute_BOQ_expected_duration_per_days')
    output_product = fields.Char()
    quantity = fields.Float(default=1)
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

    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self :
            if rec.quantity == 0 :
                raise ValidationError("Quantity must be grater than zero")

# start costing fields

    total_material_cost = fields.Float(compute='_compute_total_material_cost', store=True)
    total_equipment_cost = fields.Float(compute='_compute_total_equipment_cost', store=True)
    total_labor_cost = fields.Float(compute='_compute_total_labor_cost', store=True)
    total_overhead_cost = fields.Float(compute='_compute_total_overhead_cost', store=True)
    total_cost = fields.Float(compute='_compute_total_cost', store=True)
    additional_expense = fields.Float(compute='_compute_additional_expense', store=True)
    total_cost_and_expense = fields.Float(compute='_compute_total_cost_and_expense', store=True)
    costing_risk = fields.Float(string="Risk", compute='_compute_costing_risk', store=True)
    cost_per_unit = fields.Float(compute='_compute_cost_per_unit', store=True)
    total_costing = fields.Float(compute='_compute_total_costing')

    @api.depends('material_ids.cost_price_sub_total')
    def _compute_total_material_cost(self):
        for rec in self:
            rec.total_material_cost = sum(rec.material_ids.mapped('cost_price_sub_total')) 
            
    @api.depends('equipment_ids.sub_total')
    def _compute_total_equipment_cost(self):
        for rec in self:
            rec.total_equipment_cost = sum(rec.equipment_ids.mapped('sub_total'))
            
    @api.depends('labor_ids.sub_total')
    def _compute_total_labor_cost(self):
        for rec in self:
            rec.total_labor_cost = sum(rec.labor_ids.mapped('sub_total'))  

    
    @api.depends('over_head_ids.sub_total')
    def _compute_total_overhead_cost(self):
        for rec in self:
            rec.total_overhead_cost = sum(rec.over_head_ids.mapped('sub_total'))

    @api.depends('total_material_cost', 'total_equipment_cost', 'total_labor_cost', 'total_overhead_cost')
    def _compute_total_cost(self):
        for rec in self :
            rec.total_cost = rec.total_material_cost + rec.total_equipment_cost + rec.total_labor_cost + rec.total_overhead_cost

    @api.depends('additional_expenses_value', 'total_cost', 'additional_expenses_type')
    def _compute_additional_expense(self):
        for rec in self :
            if rec.additional_expenses_type == 'percentage' :
                rec.additional_expense = (rec.additional_expenses_value/100) * rec.total_cost
            else :
                rec.additional_expense = rec.additional_expenses_value

    @api.depends('total_cost', 'additional_expense')
    def _compute_total_cost_and_expense(self):
        for rec in self:
            rec.total_cost_and_expense = rec.total_cost + rec.additional_expense 

    @api.depends('total_cost_and_expense', 'risk')
    def _compute_costing_risk(self):
        for rec in self :
            rec.costing_risk = (rec.risk/100) * rec.total_cost_and_expense

    @api.depends('total_costing', 'quantity')
    def _compute_cost_per_unit(self):
        for rec in self :
            try:
                rec.cost_per_unit = rec.total_costing / rec.quantity
            except:
                # raise UserError("Quantity must be grater than zero")
                rec.cost_per_unit = 0
    @api.depends('total_cost_and_expense', 'costing_risk')
    def _compute_total_costing(self):
        for rec in self :
            rec.total_costing = rec.total_cost_and_expense + rec.costing_risk
# end costing fields 

# start pricing fields

    pricing_margin = fields.Float(compute='_compute_pricing_margin', store=True)
    price_per_unit = fields.Float(compute='_compute_price_per_unit', store=True)
    total_price = fields.Float(compute='_compute_total_price', store=True)


    @api.depends('total_costing', 'margin')
    def _compute_pricing_margin(self):
        for rec in self:
            rec.pricing_margin = (rec.margin/100) * rec.total_costing 

    @api.depends('total_price', 'quantity')
    def _compute_price_per_unit(self):
        for rec in self:
            try:
                rec.price_per_unit = rec.total_price / rec.quantity
            except:
                rec.price_per_unit = 0
                # raise UserError("There is something wrong !!")

    @api.depends('total_costing', 'pricing_margin')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.total_costing + rec.pricing_margin


# end pricing fields 

    @api.model
    def create(self,vals):
        res = super(CostSheet,self).create(vals)
        if res.ref == 'New' :
            res.ref = self.env['ir.sequence'].next_by_code('cost_sheet_seq')
        return res    

    @api.depends('expected_end_date')
    def _compute_BOQ_expected_duration_per_days(self):
        for rec in self:
            if rec.expected_start_date and rec.expected_end_date:
                rec.BOQ_expected_duration_per_days = (rec.expected_end_date - rec.expected_start_date).days
            else:
                rec.BOQ_expected_duration_per_days = 0



class Material(models.Model):
    _name = 'material.material'
    cost_sheet_id = fields.Many2one('cost.sheet')

    product_id = fields.Many2one('product.template')
    description = fields.Char()
    factor = fields.Float()
    planned_quantity = fields.Float(compute='_compute_planned_quantity')
    wastage = fields.Float(string="Wastage %")
    quantity_after_wastage = fields.Float(compute='_compute_quantity_after_wastage')
    cost_per_uom = fields.Float(related='product_id.standard_price')
    cost_price_sub_total = fields.Float(compute='_compute_cost_price_sub_total', store=True)

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

    equipment_id = fields.Many2one('maintenance.equipment')
    no_of_required_equipment = fields.Float()
    total_working_hours = fields.Float()
    cost_per_hour = fields.Float()
    sub_total = fields.Float(compute='_compute_sub_total', store=True)

    @api.depends('total_working_hours', 'cost_per_hour')
    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.no_of_required_equipment * rec.total_working_hours * rec.cost_per_hour

class Labor(models.Model):
    _name = 'labor.labor'

    cost_sheet_id = fields.Many2one('cost.sheet')

    job_position_id = fields.Many2one('hr.job')
    description = fields.Char()
    no_of_manpower = fields.Integer()
    total_working_hours = fields.Float()
    cost_per_hour = fields.Float()
    sub_total = fields.Float(compute='_compute_sub_total', store=True)

    @api.depends('no_of_manpower', 'total_working_hours', 'cost_per_hour')
    def _compute_sub_total(self):
        for rec in self :
            rec.sub_total = rec.no_of_manpower * rec.total_working_hours * rec.cost_per_hour 


class OverHead(models.Model):
    _name = 'over.head'

    cost_sheet_id = fields.Many2one('cost.sheet')

    product_id = fields.Many2one('product.template')
    description = fields.Char()
    planned_quantity = fields.Float()
    UOM_id = fields.Many2one('uom.uom')
    cost_per_unit = fields.Float()
    sub_total = fields.Float(compute='_compute_sub_total', store=True)

    @api.depends('planned_quantity', 'cost_per_unit')
    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.planned_quantity * rec.cost_per_unit

