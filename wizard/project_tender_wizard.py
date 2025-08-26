from odoo import api, fields, models
import pandas as pd
import io
import base64
from odoo.exceptions import UserError, ValidationError

class ImportJobOrderWizard(models.TransientModel):
    _name = 'import.job.order.wizard'
    _description = 'Wizard to Import Job Orders from Excel'

    project_tender_id = fields.Many2one('project.tender')

    excel_file = fields.Binary(string='Upload Excel File', required=True)

    def _get_uom_id(self, uom_name):
        uom = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
        if not uom:
            raise UserError(f"Unit of Measure '{uom_name}' not found.")
        return uom.id


    def import_excel(self):
        """ using pandas python package access the fields data and create job.order lines
            1) base64.b64decode() => convert binary data to it's original 
            2) read_excel(io.BytesIO(file_content), engine='openpyxl') => read the file 
        
        """
        file_content = base64.b64decode(self.excel_file)
        df =  pd.read_excel(io.BytesIO(file_content), engine='openpyxl')  
        # value = df.iloc[0, 0]

        for index, row in  df.iterrows() :
            try:
                self.env['job.order'].create({
                    'project_tender_id': self.project_tender_id.id,
                    'product': row['product'],
                    'description': row['description'],
                    'quantity': int(row['quantity']),
                    'UOM_id': self._get_uom_id(row['UOM']),
                })
            except:
                raise UserError(" You Entered Something Wrong ")





























# from odoo import models, fields, api
# import base64
# import openpyxl
# import io


# class ImportButton(models.TransientModel):
#     _name = 'import.button'

#     project_tender_id = fields.Many2one('project.tender')


#     excel_file = fields.Binary("Excel File", required=True)



#     def action_import(self):
#         active_id = self.env.context.get('active_id')
#         # record = self.env['your.model'].browse(active_id)

#         # Decode and load the Excel file
#         file_content = base64.b64decode(self.excel_file)
#         wb = openpyxl.load_workbook(filename=io.BytesIO(file_content))
#         sheet = wb.active

#         # print(file_content)
#         print(f"the neeed obj {wb}")
#         # print(sheet)

#         # lines = []
#         # for row in sheet.iter_rows(min_row=2, values_only=True):  # skip header
#         #     product_name = row[0]
#         #     quantity = row[1]

#             # product = self.env['product.product'].search([('name', '=', product_name)], limit=1)
#             # if not product:
#             #     continue

#             # lines.append((0, 0, {
#             #     'product_id': product.id,
#             #     'quantity': quantity,
#             # }))

#         # record.line_ids = lines
#         # return {'type': 'ir.actions.act_window_close'}




#             # workbook = xlrd.open_workbook(file_contents=base64.b64decode(self.excel_file))
#             # sheet = workbook.sheet_by_index(0)

#             # project_tender_id = self.env.context.get('active_id')
#             # project_tender = self.env['project.tender'].browse(project_tender_id)

#             # for row_idx in range(1, sheet.nrows):  # Skip header row
#             #     row = sheet.row_values(row_idx)
                
#             #     # Get product by name
#             #     product = self.env['product.template'].search([('name', '=', row[0])], limit=1)
#             #     # Get UOM by name
#             #     uom = self.env['uom.uom'].search([('name', '=', row[3])], limit=1)

#             #     # Create job order line
#             #     self.env['job.order'].create({
#             #         'project_tender_id': project_tender_id,
#             #         'product': product.id,
#             #         'description': row[1],
#             #         'quantity': int(row[2]),
#             #         'UOM': uom.id,
#             #     })

#             # return {'type': 'ir.actions.act_window_close'}

#     # def action_import_lines(self):
#     #     active_id = self.env.context.get('active_id')
#     #     record = self.env['your.model'].browse(active_id)

#     #     # Decode and load the Excel file
#     #     file_content = base64.b64decode(self.excel_file)
#     #     wb = openpyxl.load_workbook(filename=io.BytesIO(file_content))
#     #     sheet = wb.active

#     #     lines = []
#     #     for row in sheet.iter_rows(min_row=2, values_only=True):  # skip header
#     #         product_name = row[0]
#     #         quantity = row[1]

#     #         product = self.env['product.product'].search([('name', '=', product_name)], limit=1)
#     #         if not product:
#     #             continue

#     #         lines.append((0, 0, {
#     #             'product_id': product.id,
#     #             'quantity': quantity,
#     #         }))

#     #     record.line_ids = lines
#     #     return {'type': 'ir.actions.act_window_close'}