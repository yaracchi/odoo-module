import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from .nshift_pickup_request import nshiftCheckout
import json


DEBUG = logging.getLogger(__name__).debug
 
class SaleOrder(models.Model):
    _inherit = "sale.order"
    """
    Fields added in order to store the shipping pickup location selected when adding a shipping method
    """
    delivery_location_name = fields.Char('Delivery Location', readonly = True)
    delivery_location_zip = fields.Char('Delivery Location Zip', readonly = True) #this field to use by stock picking
    delivery_location_city = fields.Char('Delivery Location City', readonly = True)
    delivery_location_country =fields.Char('Delivery Location Country', readonly = True)
    delivery_location_addr1 =fields.Char('Delivery Location Street', readonly = True)
  