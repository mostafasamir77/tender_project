from odoo import fields, models, api

class CostSheet(models.Model):
    _name = 'cost.sheet'

    ref = fields.Char(readonly=True)
    name = fields.Char()
    product_id = fields.Many2one()