import random
import asyncio

from flight.additions.cache_operations import check_status
from flight.additions.cache_operations import check_search_existance
from flight.additions.cache_operations import set_search_data
from flight.additions.cache_operations import check_if_direction_was_searched
from flight.models import get_system_name

############################## INTEGRATIONS ####################################

from flight.suppliers.mixvel.mixvel_integration import MixvelIntegration

INTEGRATIONS = {
    'aerticket': MixvelIntegration,
    'amadeus'  : MixvelIntegration,
    'centrum'  : MixvelIntegration,
    'mixvel'   : MixvelIntegration,
}

################################################################################

CABIN_TYPES = {
    'economy' : 'Economy',
    'business': 'Business'
}

class SearchController:

    ''' A class that routes search request according to provider id '''

    def __init__(self, data) -> None: # Constructor
        self.request_id = "%0.10d" % random.randint(0, 2147483647)
        self.data = data

    async def controller(self): # Router
        trip_type = "RT" if len(self.data.get('directions')) == 2 else ("OW" if len(self.data.get('directions')) == 1 else "MC")

        result = {
            "request_id": None,
            "status": None,
            "message": []
        }

        request_check = await asyncio.create_task(check_if_direction_was_searched(data=self.data, request_id=self.request_id))
        if request_check['has']:
            result["request_id"] = request_check['request_id']
            result["status"] = "success"

            for provider in self.data.get('providers'):
                offers = await asyncio.create_task(check_search_existance(provider_id=provider['provider_id'], data=self.data, request_id=request_check['request_id']))
                if offers:
                    data = {
                        'message': 'success',
                        'data': 'found data'
                    }
                    result['message'].append(data)
            
            return result
        
        await asyncio.create_task(set_search_data(data=self.data, request_id=self.request_id, trip_type=trip_type, currency="USD", sort_type=self.data['sort_type']))
        
        result['request_id'] = self.request_id

        providerList = []
        for provider in self.data.get('providers'):
            offers = await asyncio.create_task(check_search_existance(provider_id=provider['provider_id'], data=self.data, request_id=self.request_id))

            if not offers:
                system_name = await asyncio.create_task(get_system_name(db_name='test_content', system_id=provider['system_id']))
                if system_name is not None and system_name in INTEGRATIONS:
                    integration = INTEGRATIONS[system_name](provider['auth_data'], self.data)
                    data = {
                        'integration'  : integration,
                        'provider_id'  : provider['provider_id'],
                        'provider_name': provider['provider_name'],
                        'system_id'    : provider['system_id']
                    }
                    providerList.append(data)
                else:
                    data = {
                        'message': 'error',
                        'data': 'Integration not found. system_id seems to be wrong!'
                    }
                    result['message'].append(data)
            else:
                data = {
                    'message': 'success',
                    'data': 'found data'
                }
                result['message'].append(data) 
            
        try:
            await asyncio.gather(*[task['integration'].search(task['system_id'], task['provider_id'], task['provider_name'], self.request_id) for task in providerList])
        except Exception as e:
            raise e

        result['status'] = await asyncio.create_task(check_status(request_id=self.request_id))
        
        return result

