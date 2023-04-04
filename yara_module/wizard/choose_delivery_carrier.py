from odoo import fields, models, api, _
import json
import logging

DEBUG = logging.getLogger(__name__)

class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'
    
    #office_id = fields.Many2many('choose.delivery.office', string='Office Address', default =[])
    #office_address = fields.Char(related="choose_delivery_office.delivery_office_selection")
    
    @api.onchange("carrier_id")
    def get_suggestions(self):
        """
        This function is launched when a delivery carrier is selected as a shipping method.
        It sends a request to 3rd party to ask for a list of the nearest pickup locations of 
        the delivery based on the customer's zipcode.
        """
            
        context = self.env.context
        delivery_carrier_wizard_id = context.get('active_id')
        delivery_carrier_wizard = self.env['choose.delivery.carrier'].search([('id', '=', delivery_carrier_wizard_id)], limit=1) #call current wizard record
        selected_carrier = delivery_carrier_wizard.carrier_id
        sale_order = delivery_carrier_wizard.order_id
        
        if selected_carrier:
           
            # test sample
            agents = [
                {
                "id": "74383",
                "name": "Agent name1",
                "address1": "Agentstreet 1",
                "address2": 'null',
                "zipCode": "11111",
                "city": "STOCKHOLM",
                "country": "SE"
                },
                {
                "id": "43333",
                "name": "Agent name2",
                "address1": "Agentstreet 2",
                "address2": 'null',
                "zipCode": "11111",
                "city": "STOCKHOLM",
                "country": "SE"
                }
              ]
            locations_selection = []
            #prepare the list of locations (agents)
            for agent in agents:
                # define object of agent (adress info) 
                pickup_location_information ={
                    'name': agent['name'],
                    'zip': agent['zipCode'],
                    'city': agent['city'],
                    'address1': agent['address1'],
                    'address2' : agent['address2'],
                    'country' : agent['country']
                }
                label = agent['name'] + ' ' +agent['address1'] + ' ' + agent['zipCode']+ ' '+agent['city']+ ' '+agent['country'] 
                #make it as a json object 
                locations_selection.append(tuple([json.dumps(pickup_location_information), label]) )
            
            #pass the list of locations to office wizard via context 
            self.env.context = dict(self.env.context)
            self.env.context.update({
            'default_locations': locations_selection,
             })
                
            return { 
            'locations_selection': locations_selection,
            } 
        
        else:
            return { 
                'locations': [('no pickup office','no pickup office')],
                }

    def button_confirm(self):
        """
        This function is inherited to update the sale order with the selected  
        delivery pickup location from the choose_carrier_office wizard. 
        """

        res = super(ChooseDeliveryCarrier, self).button_confirm()
        sale_order_id = self.env.context.get('default_order_id') 
        sale_order = self.env['sale.order'].search([('id', '=', sale_order_id)], limit=1)
        location = self.env.context.get('default_office_selection')

        if location:
            #transorm to json
            data = json.loads(location)
            data_update_order = {
                "name" : data['name'],
                "address1"  : data['address1'],
                "address2"  : data['address2'],
                "city"      : data['city'],
                "zip"       : data['zip'],
                "country"   :  data['country']
            }
            #update sale order
            delivery_location_info = {
                'delivery_location_name' : data_update_order['name'],
                'delivery_location_zip' :  data_update_order['zip'],
                'delivery_location_country' : data_update_order['country'], 
                'delivery_location_addr1' :  data_update_order['address1'],
                'delivery_location_city' :  data_update_order['city'],
            }
            sale_order.write(delivery_location_info)

        return res
