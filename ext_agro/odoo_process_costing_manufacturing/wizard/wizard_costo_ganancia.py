from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp
import logging

import io
from io import BytesIO

import xlsxwriter
import shutil
import base64
import csv
import xlwt

_logger = logging.getLogger(__name__)

class CostoGananciaModelo(models.Model):
    _name = "stock.wizard.pdf.costogana"

    name = fields.Date(string='Fecha')
    product_id = fields.Many2one('product.template', 'Productos')
    cantidad = fields.Float()
    costo_unit=fields.Float()
    sub_total = fields.Float()

class costo_ganancia(models.TransientModel):
    _name = "stock.wizard.costo.ganancia" ## = nombre de la carpeta.nombre del archivo deparado con puntos

    date_from = fields.Date(string='Date From', default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    date_to = fields.Date('Date To', default=lambda *a:(datetime.now() + timedelta(days=(1))).strftime('%Y-%m-%d'))
    line  = fields.Many2many(comodel_name='stock.wizard.pdf.costogana', string='Lineas')

    def print_costo_ganancia(self):
        self.env['stock.wizard.pdf.costogana'].search([]).unlink()
        self.lista_producto()

    def lista_producto(self):
        cursor_resumen = self.env['product.template'].search([('sale_ok','=','True')],order ="id ASC")
        t=self.env['stock.wizard.pdf.costogana']
        d=t.search([])
        for det in cursor_resumen:
            values={
            'name':"2021-01-01",
            'product_id':det.id,
            'cantidad':self.busca_cantidad(det),
            'costo_unit':det.standard_price,
            'sub_total':self.busca_sub(det),
            }
            pdf_id = t.create(values)
        self.line = self.env['stock.wizard.pdf.costogana'].search([])

    def busca_cantidad(self,dett):
        quantity=0
        lista_fact=self.env['account.move.line'].search([('product_id','=',dett.id)])
        if lista_fact:
            for det_list in lista_fact:
                if det_list.move_id.type=="out_invoice" or det_list.move_id.type=="out_refund" or det_list.move_id.type=="out_receipt":
                    quantity=quantity+det_list.quantity
        return quantity

    def busca_sub(self,dett):
        sub_totales=0
        lista_fact=self.env['account.move.line'].search([('product_id','=',dett.id)])
        if lista_fact:
            for det_list in lista_fact:
                if det_list.move_id.type=="out_invoice" or det_list.move_id.type=="out_refund" or det_list.move_id.type=="out_receipt":
                    sub_totales=sub_totales+det_list.price_subtotal
        return sub_totales
