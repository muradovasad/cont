from datetime import datetime
import uuid


class Validator:

    async def search_request_valiadator(data: dict) -> bool:
        directions = data.get('directions', None)
        providers = data.get('providers', None)
        adt = data.get('adt', False)
        chd = data.get('chd', None)
        inf = data.get('inf', None)
        ins = data.get('ins', None)
        clas = data.get('class', None)
        flexible = data.get('flexible', None)
        direct = data.get('direct', None)

        if directions == None or providers == None or adt == False or chd == None or inf == None or ins == None or clas == None or flexible == None or direct == None:
            return False

        are_dirs_correct = True
        if directions != None and isinstance(directions, list):
            for dir in directions:
                if not dir.get('departure_airport', False):
                    are_dirs_correct = False
                    break
                if not dir.get('arrival_airport', False):
                    are_dirs_correct = False
                    break
                if not dir.get('departure_date', False):
                    are_dirs_correct = False
                    break
        else:
            are_dirs_correct = False

        are_providers_correct = True
        if providers != None and isinstance(providers, list):
            for prov in providers:
                if not prov.get('system_id', False):
                    are_providers_correct = False
                    break
                if not prov.get('provider_id', False):
                    are_providers_correct = False
                    break
                if not prov.get('provider_name', False):
                    are_providers_correct = False
                    break
                if not prov.get('auth_data', False):
                    are_providers_correct = False
                    break
        else:
            are_providers_correct = False

        is_count_correct = True

        if inf + ins > adt or adt + chd + ins > 9:
            is_count_correct = False
                
        return (adt and chd != None and inf != None and ins != None and clas != None and flexible != None and direct != None and are_dirs_correct and is_count_correct and are_providers_correct)

    async def offers_request_valiadator(data: dict) -> bool:
        request_id = data.get('request_id', None)
        next_token = data.get('next_token', 0)

        return (request_id != None and next_token != 0) 

    async def booking_request_validator(data: dict) -> bool:
        pass
    
    async def adding_new_system_validator(data: dict) -> bool:
        system_id = data.get('system_id', False)
        system_name = data.get('system_name', False)
        auth_data = data.get('auth_data_fields', False)

        return await Helper.is_valid_uuid(system_id) and isinstance(system_name, str) and isinstance(auth_data, list)

class Formatter:

    async def str_to_datetime(data):
        date_object = datetime.strptime(data, '%Y-%m-%d').date()
        return date_object
    
    async def time_to_year(date):
        pass

    async def year_to_time(date):
        pass

    async def format_routes(data):
        pass

class Helper:

    async def currency_converter(curFrom, curTo):
        if curFrom == curTo:
            return 1
        else:
            return 1200
        
    async def is_valid_uuid(string):
        try:
            uuid_obj = uuid.UUID(string)
            return str(uuid_obj) == string
        except ValueError:
            return False

class AdditionsTicket:

    def __init__(self, ticket, offer_id, other, gds_id, sp_name) -> None:
        self.ticket   = ticket
        self.offer_id = offer_id
        self.other    = other
        self.gds_id   = gds_id
        self.sp_name  = sp_name
