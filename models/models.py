# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class dhb_mrp_product_prod(models.Model):
     _inherit = "product.template"

     width = fields.Float(string="width")
     length = fields.Float(string="length")
     type = fields.Selection([('consu', _('Consumable')),('service', _('Service')),('product', _('Product'))],default='product')

class dhb_mrp_sales_order_line(models.Model):
    _inherit = "sale.order.line"

    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True),('purchase_ok', '=', False),('type', '=', 'product')])
    product_width = fields.Float('Product Width', related="product_id.width", store=True)
    product_length = fields.Float('Product Length', related="product_id.length", store=True)
    #test = fields.Char("test", compute ='test')

    @api.multi
    def test(self, context = None):
        self.ensure_one()
        context['purchase_ok'] = False
        _logger.debug("ARN text")



class dhb_mrp_sales_order_materialWizard(models.TransientModel):
    _name = 'dhb_mrp.salesorder'
    _description = 'Sales Order Material'
    sales_order_id = fields.Many2one('sale.order', string='Sale Order',size=20)
    cust_ref = fields.Char(string='Customer Reference', related='sales_order_id.client_order_ref')


    dhb_raw_material_ids = fields.One2many('dhb_mrp.sales_raw_materials','parent_id')
    dhb_final_prod_ids = fields.One2many('dhb_mrp.sales_final_prod', 'parent_id')


    @api.multi
    def _reopen_form(self):
        self.ensure_one()

        action = {
            'type': 'ir.actions.act_window',
            'name' : self._description ,
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return action



    @api.multi
    def do_calculation(self):
        self.ensure_one()

        for record in self.dhb_raw_material_ids:
            _logger.debug('arn borrando linked records')
            record.unlink()


        for record in self.dhb_final_prod_ids:
            _logger.debug('arn borrando linked records')
            record.unlink()


        _logger.debug('calculation detail %s' % self.sales_order_id)
        # Values to Write

        for sales_lines in self.sales_order_id.order_line:
            self.dhb_final_prod_ids.create({'product_name': sales_lines.product_id.product_tmpl_id.name,
                                          'qty_to_consume': sales_lines.product_uom_qty,
                                              'width' : sales_lines.product_width,
                                              'lenght' : sales_lines.product_length,
                                          'parent_id': self.id})





        production_orders = self.env['mrp.production']
        raw_materials = self.env['stock.move']
        sales_name_origen = self.sales_order_id.name
        _logger.debug("ARN name origien is " + str(sales_name_origen))
        #sales_name_origen = sales_order.search_read([('id', '=', self.sales_order_id.id),('date', '<', self.date_from)], ['residual_signed'])



        production_order_aux = production_orders.search([('origin', '=', self.sales_order_id.name),('state', 'in', ['progress','confirmed'])])
        #self.env.invalidate_all()
        _logger.debug("ARN currose is " + str(production_order_aux))
        #prod_tuple = ()
        prod_list = [];
        for h in production_order_aux:
            if h.move_raw_ids:
                for j in h.move_raw_ids:
                    _logger.debug("ARN currose is2  " + str(j.id))
                    prod_list.append(j.id)
        prod_tuple = tuple(prod_list)
        prod_tuple = (prod_tuple,)
        #prod_tuple = ()
        #prod_tuple = (sales_name_origen,)
        #_logger.debug ("Arn is tuple " + str(prod_tuple))


        #move_order_aux = self.env.cr.execute("select product_id , sum(product_uom_qty) from stock_move where id in %s order by product_id group by product_id",production_order_aux.move_row_ids )
        _logger.debug ("ARn tupĺe with ids is " + str(prod_tuple))
        self.env.cr.execute("select product_id , sum(product_uom_qty) from stock_move where id IN %s group by product_id ",prod_tuple)
        #self.env.cr.execute("select id,  product_id , product_uom_qty from stock_move")

        move_order_aux = self.env.cr.fetchall()
        # data = {
        #
        #     "move_order_aux": move_order_aux.fetchall()
        #
        # }
        _logger.debug ( "ARN new currose is " + str (move_order_aux))
        #_logger.debug("ARN data is " + str(data))
        _logger.debug("ARN after search " )

        acum_product_oum_qty = 0
        acum_reserved_availability = 0
        acum_availability = 0

        if move_order_aux:
            product_ant = move_order_aux[0][0]

            for prod_order in move_order_aux:

                prod_names = self.env['product.product']
                prod_name = prod_names.search([('id', '=', product_ant)])
                prod_name_aux = prod_name.product_tmpl_id.name

                if prod_order[0] == product_ant:
                    acum_product_oum_qty = acum_product_oum_qty + prod_order[1]
                else:

                    self.dhb_raw_material_ids.create({'product_name': prod_name_aux ,
                                                      'qty_to_consume': acum_product_oum_qty,
                                                      'qty_reserved': 0,
                                                      'qty_consumed': 0,
                                                      'parent_id': self.id})
                    acum_product_oum_qty = prod_order[1]

                product_ant = prod_order[0]

                _logger.debug("ARN totales acum_product_oum_qty" + str (acum_product_oum_qty))


        # for raw_mat in prod_order.move_raw_ids:
        #     _logger.debug("ARn pre execution of _compute_reserved_availability")
        #
        #     _logger.debug("ARN value is raw_mat " + str(raw_mat))
        #     _logger.debug("ARN value is raw_mat " + str(raw_mat.product_id.product_tmpl_id.name))
        #     _logger.debug("ARN value is raw_mat " + str(raw_mat.availability))
        #     _logger.debug("ARN value is raw_mat " + str(raw_mat.reserved_availability))
        #     self.dhb_raw_material_ids.create({'product_name': raw_mat.product_id.product_tmpl_id.name,
        #                                         'qty_to_consume': raw_mat.product_uom_qty,
        #                                         'qty_reserved': raw_mat.reserved_availability,
        #                                         'qty_consumed': raw_mat.availability,
        #                                         'parent_id': self.id})

        #
        # for prod_order in production_order_aux:
        #     if prod_order.move_raw_ids:
        #         product_ant =  prod_order.move_raw_ids[0].product_id
        #         acum_product_oum_qty = 0
        #         acum_reserved_availability = 0
        #         acum_availability = 0
        #         for raw_mat in prod_order.move_raw_ids:
        #             if raw_mat.product_id == product_ant:
        #                 acum_product_oum_qty = acum_product_oum_qty + raw_mat.product_uom_qty
        #                 acum_reserved_availability = acum_reserved_availability + raw_mat.reserved_availability
        #                 acum_availability = acum_availability + raw_mat.availability
        #             else:
        #                 acum_product_oum_qty = raw_mat.product_uom_qty
        #                 acum_reserved_availability = raw_mat.reserved_availability
        #                 acum_availability = raw_mat.availability
        #
        #             _logger.debug("ARN totales acum_product_oum_qty" + str (acum_product_oum_qty))
        #             _logger.debug("ARN totales acum_reserved_availability" + str(acum_reserved_availability))
        #             _logger.debug("ARN totales acum_availability" + str(acum_availability))
        #
        #
        #         for raw_mat in prod_order.move_raw_ids:
        #             _logger.debug("ARn pre execution of _compute_reserved_availability")
        #             raw_mat._compute_reserved_availability
        #             raw_mat._compute_product_availability
        #
        #
        #             _logger.debug("ARN value is raw_mat " + str(raw_mat))
        #             _logger.debug("ARN value is raw_mat " + str(raw_mat.product_id.product_tmpl_id.name))
        #             _logger.debug("ARN value is raw_mat " + str(raw_mat.availability))
        #             _logger.debug("ARN value is raw_mat " + str(raw_mat.reserved_availability))
        #             self.dhb_raw_material_ids.create({'product_name': raw_mat.product_id.product_tmpl_id.name,
        #                                                 'qty_to_consume': raw_mat.product_uom_qty,
        #                                                 'qty_reserved': raw_mat.reserved_availability,
        #                                                 'qty_consumed': raw_mat.availability,
        #                                                 'parent_id': self.id})
        #



        return self._reopen_form()


#         self.balance_ini =  0
#         if amounts:
#             _logger.debug('arn  movements to calculate initial bal are ' + str(amounts))
#             #for h in amounts:
#             self.balance_ini = sum(h.get('residual_signed') for h in amounts)
#             _logger.debug('arn sum for initial balance is ' + str(self.balance_ini))
#         else:
#             self.balance_ini = 0
#
#
#         # for j in amounts:
#         #     _logger.debug('ARN value is ' + str(j))
#         #     if j['residual_signed']:
#         #         monto = monto + j['residual_signed']
#         #
#         #     _logger.debug('ARN value is for residual' + str(j['residual_signed']))
#         #     _logger.debug('ARN value is for monto inicial' + str(monto))
#         #amounts = 0
#         #self.balance_ini = monto
#         _logger.debug("ARN value is " + str(amounts))
#         _logger.debug("ARN value for balance ini is %s" % str(self.balance_ini))
#         partner_aux_id = self.partner_id.id
#         date_from_aux = self.date_from
#         #self.auxiliar_detalle_ids.delete
#         for record in self.dhb_raw_material_ids:
#             _logger.debug('arn borrando linked records')
#             record.unlink()
#
#
#
#         _logger.debug ('ARN date and partner id ' + str(date_from_aux) + ' ' + str(partner_aux_id))
#         account_move = self.env['account.move']
#         account_moves = account_move.search([('partner_id', '=', partner_aux_id),('date', '>=', date_from_aux)],
#                                             order='date , create_date asc')
#         _logger.debug('arn account moves for the partner ' + str(account_moves))
#
#         saldo_actual = self.balance_ini
#         if account_moves:
#             for h in account_moves:
#                 _logger.debug('arn inside account moves id and journal id' + str(h.id) + ' amount  ' + str(h.amount) + " journal " + str(h.journal_id))
#                 if h.journal_id.type in ("sale","bank"):
#                     saldo_actual = saldo_actual - h.amount
#                     self.auxiliar_detalle_ids.create({'amount_debit': h.amount,
#                                                       'amount_credit': 0,
#                                                       'document_no' : h.document_number ,
#                                            raw_materials = self.env['stock.move']
#         #account_1 = 1
#         monto = 0
#         _logger.debug("ARN value is " + str(raw_materials))
#         raw_materials_aux = raw_materials.search_read([('partner_id', '=', self.partner_id.id),('date', '<', self.date_from)], ['residual_signed'])               'date' : h.date ,
#                                                       'current_balance' : saldo_actual ,
#                                                       'parent_id': self.id})
#                 else:
#                     saldo_actual = saldo_actual + h.amount
#                     self.auxiliar_detalle_ids.create({'amount_debit': 0,
#                                                       'amount_credit': h.amount,
#                                                       'document_no': h.document_number,
#                                                       'date': h.date,
#                                                       'current_balance': saldo_actual,
#                                                       'parent_id': self.id})
#         else:
#             self.auxiliar_detalle_ids.create({'amount_debit': 0,
#                                               'amount_credit': 0,
#                                               'document_no': 'SIN MOVIMIENTOS',
#                                               'current_balance': saldo_actual,
#                                               'parent_id': self.id})
#
#             #self.auxiliar_detalle_ids.create({'amount_test': h.amount, 'parent_id': self.id})
#             #self.auxiliar_detalle_ids.amount_test = h.amount
#         self.balance_fin = saldo_actual
#
#
#
#
#         #time.sleep(10)
#         return self._reopen_form()
#

class dhb_final_prod(models.TransientModel):
    _name = 'dhb_mrp.sales_final_prod'
    _description = 'sales order final products'

    parent_id = fields.Many2one(comodel_name='dhb_mrp.salesorder')
    product_name = fields.Char(string="product")
    qty_to_consume = fields.Float(string="Quantity to consume")
    width =fields.Float(string="Width")
    length = fields.Float(string="Lenght")



class dhb_raw_materials(models.TransientModel):
    _name = 'dhb_mrp.sales_raw_materials'
    _description = 'sales order raw materials'

    parent_id = fields.Many2one(comodel_name='dhb_mrp.salesorder')
    product_name = fields.Char(string="product")
    qty_to_consume = fields.Float(string="Quantity to consume")
    qty_reserved = fields.Float(string="Quantity reserved")
    qty_consumed = fields.Float(string="Quantity consumed")
#      #product_name = fields.Char(string="product")
#      #product_name = fields.Char(string="product")
#
#
#      # account_1 = 1
#
#
#      # amount_debit = fields.Float(string="monto al debe")
#      # amount_credit = fields.Float(string="monto al haber")
#      # date = fields.Date("fecha de mov")
#      # document_no =fields.Char("N° Documento")
#      # current_balance = fields.Float ("Saldo Actual")
#
#      #document_number = fields.Many2one(comodel_name='account.move', string="invoice ")
#
#
#
# #     partner_id = fields.Many2one('res.partner', string='Cliente/Proveedor',size=50)
# #     date_from = fields.Date(string='fecha desde',size=20)
#
#
#
#
