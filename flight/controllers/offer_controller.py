import json
import asyncio

from flight.additions.cache_operations import check_status
from flight.additions.cache_operations import check_offers_existance, get_search_data

class OfferController:
    
    def __init__(self, data: dict) -> None: # Constructor
        self.request_id = data.get('request_id', None)
        self.next_token = data.get('next_token', None)

    async def controller(self): # Router
        result = {
            "request_id": None,
            "status": None,
            "message": [],
            "trip_type": "",
            "sort_type": "",
            "currency": "USD",
            "next_token": None,
            "offers": []
        }

        search_data = await asyncio.create_task(get_search_data(request_id=self.request_id))

        if search_data != None:
            search_data = json.loads(search_data)
            result['status']     = await asyncio.create_task(check_status(request_id=self.request_id))
            result['request_id'] = self.request_id
            result['trip_type']  = search_data['trip_type']
            result['currency']   = search_data['currency']
            result['sort_type']  = search_data['sort_type']

            offers = await asyncio.create_task(check_offers_existance(request_id=self.request_id))
            if offers: 
                data = {
                    'message': 'success',
                    'data': 'found data'
                }
                result['offers'] = offers
                result['message'].append(data) 
            else:
                result['status'] = 'error'
                data = {
                    'message': 'error',
                    'data': 'data not found!'
                }
                result['message'].append(data)            
        else:
            result['status'] = 'error'
            data = {
                'message': 'error',
                'data': 'data not found! request_id is not valid or direction was not searched' 
            }
            result['message'].append(data)

        if result['sort_type'] == 'price':
            result['offers'] = await asyncio.create_task(self.sort_by_price(offers))

        return result
    
    async def sort_by_price(self, offers):
        return sorted(offers, key=lambda offer: offer["price_info"]["price"])
    
