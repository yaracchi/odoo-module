
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
import json
import urllib
import time

from odoo.http import request
DEBUG = logging.getLogger(__name__).debug

class BetterHTTPErrorProcessor(urllib.request.BaseHandler):
    def http_error_201(self, request, response, code, msg, hdrs):
        return response

    def http_error_400(self, request, response, code, msg, hdrs):
        return response

    def http_error_422(self, request, response, code, msg, hdrs):
        return response

    def http_error_500(self, request, response, code, msg, hdrs):
        return response

class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_status = fields.Char(string = "Shipping Status")

    # Schedualed action function
    def get_status_shipment(self):

        '''
        Fetch information about delivery status connected to shipments from an external API.
        Updates each delivery with its coresponding status.
        '''

        fetchId = 0
        done = False 
        base_url = 'https://api.unifaun.com/rs-extapi/v1'
        fetch_url = base_url + '/alerts?fetchId=%s'%(fetchId)
        alerts = []

        opener = urllib.request.build_opener(BetterHTTPErrorProcessor)
        urllib.request.install_opener(opener)
        data_key = 'test'

        # Check if there are more alerts to fetch
        while(not done):
            ################# This needs a valid data_key to work 
            # r = urllib.request.Request(
            #    url=fetch_url,
            #    data=None,
            #    headers={
            #        'Authorization': 'Basic %s' % data_key,
            #    }
            #)
            #u = urllib.request.urlopen(r)
            #response_http_status_code = u.getcode()
            #response = u.read().decode("utf-8")            
            #if response_http_status_code == 401:
            #    raise ValidationError(
            #        _('http code 401: Invalid or expired token.'))
            #if response_http_status_code == 403:
            #    raise ValidationError(
            #        _('http code 403: The token is valid but it doesnt grant access to the operation attempted.'))
            
            # parsing string to python object/dict 
            #response_dict = json.loads(response)
            #################

            #test sample
            response_dict={
                "fetchId": "1",
                "minDelay": 100,
                "done": True,
                "alerts": [{
                    "alertCode": "STATUS_DELIVERED",
                    "alertTime": "2015-06-03T13:18:30.000+0000",
                    "alertCreated": "2015-06-03T13:18:30.000+0000",
                    "alertInfo": "STATUS",
                    "shipmentInfo": {
                    "serviceId": "P15",
                    "shipmentNo": 'null',
                    "orderNo": "order number 123",
                    "reference": "sender ref 234",
                    "parcelCount": 1,
                    "parcels": [{
                        "parcelNo": "69563053713SE",
                        "reference": 'null'
                    }],
                    "shipDate": "2015-06-03T13:18:30.000+0000",
                    "printDate": "2015-06-03T13:18:30.904+0000"
                    }
                }]
                }

            if response_dict['alerts']:
                # Update alerts list
                alerts.extend(response_dict['alerts'])

            # Update fitchId value and detch_url to get next list
            fetchId = response_dict['fetchId']
            fetch_url = base_url + '/alerts?fetchId=%s'%(fetchId)
            done = response_dict['done']

            # Wait for minDelay to make another call 
            if (not response_dict['minDelay']*0.001 > 1):
                time.sleep(response_dict['minDelay']*0.001)        

        # Filter the list of alerts to take only latest status of each order/parcel
        if alerts:
            # Store the first and latest alert order
            latest_parcelNo = alerts[0]['shipmentInfo']['parcels'][0]['parcelNo']
            pickings_to_update = []
            pickings_to_update.append(alerts[0])

            for alert in alerts:
                parcelNo = alert['shipmentInfo']['parcels'][0]['parcelNo']

                # Skip if alert has same reference as previous one
                if parcelNo != latest_parcelNo:
                    # store the alert in list and update variable
                    pickings_to_update.append(alert)
                    latest_parcelNo = alert['shipmentInfo']['parcels'][0]['parcelNo']
        
        else:
            raise ValidationError(_('No status data was received'))
        

        # Update the delivery status of the stock pickings using carrier_tracking_ref (parcelNo in alerts)
        if pickings_to_update:
                # Stock stock pickings in a list with one query call
                pickings = request.env['stock.picking'].sudo().search([])
                for alert in pickings_to_update:
                    for picking in pickings: 
                        picking.write({
                               'delivery_status':'test status updated'
                            })
                        #if alert['shipmentInfo']['parcels'][0]['parcelNo'] ==  picking.carrier_tracking_ref :
                            #  Update the stock picking delivery status 
                           # picking.write({
                               # 'delivery_status':alert['alertCode']
                            #})
                            # Break from loop if found the searched picking
                           # break

        return pickings_to_update