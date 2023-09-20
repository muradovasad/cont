import asyncio
import os
import aiohttp
import datetime
import uuid
import json
import requests
import xmltodict
import redis
from jinja2 import Environment, FileSystemLoader

from .converter.searchConverter import search_converter
from flight.models import insert_data
from flight.additions.cache_operations import set_status, set_provider_response_to_cache
from .endpoint import is_login_endpoint, request_template

HERE = os.path.dirname(os.path.abspath(__file__))

TEST_GATEWAY = 'https://api-test.mixvel.com'

TTL = 3 * 60

CABIN_TYPES = {
    'economy': 'Economy',
    'business': 'Business'
}

class MixvelIntegration:

############################################ DEFAULT #################################################

    def __init__(self, auth_data, data, verify_ssl=True):
        self.login = auth_data.get('login', None)
        self.password = auth_data.get('password', None)
        self.structure_unit_id = auth_data.get('structure_unit_id', None)
        self.token = ""
        self.gateway = TEST_GATEWAY
        self.verify_ssl = verify_ssl
        self.data = data

    async def __prepare_request(self, template, context):
        context["message_id"] = str(uuid.uuid4())
        strftime = datetime.datetime.utcnow()
        strftime = f"{strftime.year}-{strftime.month if len(str(strftime.month)) == 2 else f'0{strftime.month}'}-{strftime.day if len(str(strftime.day)) == 2 else f'0{strftime.day}'}T{strftime.hour if len(str(strftime.hour)) == 2 else f'0{strftime.hour}'}:{strftime.minute if len(str(strftime.minute)) == 2 else f'0{strftime.minute}'}:{strftime.second if len(str(strftime.second)) == 2 else f'0{strftime.second}'}Z"
        context["time_sent"] = strftime
        template_env = Environment(loader=FileSystemLoader(os.path.join(HERE, 'templates')))
        request_template = template_env.get_template(template)
        return request_template.render(context)

    async def __request(self, endpoint, context):
        url = "{gateway}{endpoint}".format(gateway=self.gateway, endpoint=endpoint)
        headers = {
            "Content-Type": "application/xml",
        }

        if not await asyncio.create_task(is_login_endpoint(endpoint)):
            if not self.token:
                await asyncio.create_task(self.auth())
            headers["Authorization"] = "Bearer {token}".format(token=self.token)

        template = await asyncio.create_task(request_template(endpoint))

        if template is None:
            raise ValueError("Unknown endpoint: {}".format(endpoint))
        
        data = await asyncio.create_task(self.__prepare_request(template, context))
        self.sent = data
        self.recv = None

        r = await asyncio.create_task(self._send(url, headers, data))

        if r[0] in [200, 201]:
            response = xmltodict.parse(r[1], encoding='utf-8', attr_prefix='', dict_constructor=dict)
            if 'AppData' in response['MixEnv:Envelope']['Body']:
                result = {
                    'status': 'success',
                    'message': 'successful operation performed',
                    'data': response['MixEnv:Envelope']
                }
                return result
            else:
                result = {
                    'status': 'error',
                    'message': 'Unknown error occured during operation',
                    'data': r[1]
                }
            return result
        else:
            result = {
                'status': 'error',
                'message': 'Unknown error occured during operation',
                'data': r[1]
            }
            return result
    
    async def _send(self, url, headers, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers, ssl=self.verify_ssl) as response:
                status_code = response.status
                result = await response.text()
                return [status_code, result]

############################################ AUTH #################################################

    async def auth(self):
        context = {
            "login": self.login,
            "password": self.password,
            "structure_unit_id": self.structure_unit_id,
        }
        res = await asyncio.create_task(self.__request("/api/Accounts/login", context))

        token = None
        if res['status'] == 'success' and 'Token' in res['data']['Body']['AppData']['Auth:AuthResponse']:
            token = res['data']['Body']['AppData']['Auth:AuthResponse']['Token']
            self.token = token
        return token 

########################################### SEARCH ################################################

    async def search(self, system_id, provider_id, provider_name, request_id):
        data = await asyncio.create_task(self.search_request_maker())
        itinerary = data['itinerary']
        paxes     = data['paxes']

        currency = {
            'curFrom': 'UZS',
            'curTo'  : 'USD'
        }

        if itinerary and paxes:
            context = data
            res = await asyncio.create_task(self.__request("/api/Order/airshopping", context))

            if res['status'] == 'success':
                await set_status(request_id=request_id)
                result = {
                    'status' : res['status'], 
                    'massage': res['message'],
                    'data'   : await search_converter(res['data'], provider_id, provider_name, currency, len(itinerary) == 1, request_id)
                }

                # inserting data to cache
                asyncio.create_task(set_provider_response_to_cache(data=self.data, provider_id=provider_id, offer=result, request_id=request_id))
                
                # inserting data to a database for Business Intelligence
                asyncio.create_task(insert_data(system_id=system_id, provider_id=provider_id, provider_name=provider_name, offers=result))
                
                return json.dumps(result)
            else:
                result = {
                    'status' : res['status'], 
                    'massage': res['message'],
                    'data'   : res['data']
                }
                return result
        else:
            result = {
                'status' : 'error', 
                'massage': 'inaccurate data provided',
                'data'   : []
            }
            return result
 
    async def search_request_maker(self):
        data = self.data
        directions = []
        paxes = []

        for dir in data['directions']:
            directions.append(
                {
                    "origin": dir['departure_airport'],
                    "destination": dir['arrival_airport'],
                    "departure": dir['departure_date'],
                    "cabin": CABIN_TYPES[data['class']]
                }
            )
        pax = 0
        for _ in range(data['adt']):
            paxes.append({
                "pax_id": f"PAX-{pax+1}",
                "ptc": "ADT"
            })
            pax += 1

        for _ in range(data['chd']):
            paxes.append({
                "pax_id": f"PAX-{pax+1}",
                "ptc": "CNN"
            })
            pax += 1

        for _ in range(data['inf']):
            paxes.append({
                "pax_id": f"PAX-{pax+1}",
                "ptc": "INF"
            })
            pax += 1

        for _ in range(data['ins']):
            paxes.append({
                "pax_id": f"PAX-{pax+1}",
                "ptc": "INS"
            })
            pax += 1
        
        body = {
            'itinerary': directions,
            'paxes': paxes
        }
        
        return body

########################################### UPSELL ################################################

    async def upsell(self):
        pass

########################################### RULES ################################################

    async def rules(self):
        pass

########################################## BOOKING ################################################

    async def booking(self):
        pass

########################################### CANCEL ################################################

    async def cancel(self):
        pass

########################################### TICKET ################################################

    async def ticketing(self):
        pass

