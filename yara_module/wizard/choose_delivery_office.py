from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging

DEBUG = logging.getLogger(__name__)

class ChooseDeliveryOffice(models.TransientModel):
    _name = 'choose.delivery.office'
    """
    A wizard that shows the pickup locations list, that was received from api, as a selection.
    The selected pickup location will be passed to the choose_delivery_carrier wizard
    """
    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method")
    delivery_office_selection = fields.Selection(selection=lambda self:self._compute_selection(), string='Delivery Location',required=True )
    
    #compute the selection field using the result received from the api request
    def _compute_selection(self): 
        result = self.env['choose.delivery.carrier'].get_suggestions()
        return result['locations_selection'] 
    
    #recreate choose delivery carrier wizard and update its context 
    def button_confirm(self):
        self.ensure_one()
        view_id = self.env.ref('delivery.choose_delivery_carrier_view_form').id       
        if self.delivery_office_selection:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'choose.delivery.carrier',
                'res_id': self.env.context.get('active_id'),
                'view_id': view_id,
                'views': [(view_id, 'form')],
                'target': 'new',
                'context' : self.env.context
            }
        
   
