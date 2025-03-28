from odoo import api, fields, models, _
from . import barcode
import math


class DynamicProductBarcode(models.TransientModel):
    _name = 'dynamic.product.template.barcode.number'

    @api.model
    def default_get(self, fields):
        res = super(DynamicProductBarcode, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        sale_order_ids = self.env['product.template'].browse(active_ids)
        print("default_get:", sale_order_ids)
        return res


    def dynamic_product_barcode(self):
        print('Confirm barcode generator')
        self.ensure_one()
        product_ids = self.env['product.template'].browse(self._context.get('active_ids'))
        existing_code_products = []


        for prod in product_ids:
            product_id = prod.id
            product_product_ids = self.env['product.product'].search([('product_tmpl_id','=',product_id)])
            print('product_product_id:',product_product_ids)
            for prod_prod_id in product_product_ids:
                product_product_id = prod_prod_id.id
                if prod_prod_id.barcode == False or prod_prod_id == "":
                    eanbarcode = barcode.generate_ean(self, str(product_product_id))
                    self.env.cr.execute(
                        "update product_product set barcode='" + str(eanbarcode) + "' where id='" + str(product_product_id) + "'")
                else:
                    existing_code_products.append(prod_prod_id.name)

        messages = []                                    
        if existing_code_products:
            messages.append({
                'type': 'warning',
                'title': _('Advertencia'),
                'message': _('Algunos productos ya tienen código de barras: %s') % ', '.join(existing_code_products)
            })
            
        action = {'type': 'ir.actions.act_window_close'}
            
        if messages:    
            first_msg = messages[0]
            notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': first_msg['title'],
                        'message': first_msg['message'],
                        'sticky': False,
                        'type': first_msg['type'],
                        'next': action,
                    }
                }
            return notification
        return action                
        