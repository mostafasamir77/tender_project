from odoo import fields, models, api

class CostSheet(models.Model):
    _name = 'cost.sheet'

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
    ],string='Additional Expenses')
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
