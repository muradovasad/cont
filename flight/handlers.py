import json
import asyncio
import tornado.web

from flight.models import insert_system

from flight.additions.additions import Validator
from flight.controllers.search_controller import SearchController
from flight.controllers.offer_controller import OfferController

# FLIGHT HANDLERS. BE CAREFUL WHILE CHANGING THEM.

class SearchHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.search_request_valiadator(data)):
            # start_time = time.time()
            controller = SearchController(data)
            response = await asyncio.gather(controller.controller())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]
        
        # print(f"Search handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])

class OfferHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.offers_request_valiadator(data)):
            # start_time = time.time()
            controller = OfferController(data)
            response = await asyncio.gather(controller.controller())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Offer handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])

class UpsellHandler(tornado.web.RequestHandler):
    async def post(self):
        pass

class RulesHandler(tornado.web.RequestHandler):
    async def post(self):
        pass

class BookingHandler(tornado.web.RequestHandler):
    async def post(self):
        pass

class TicketingHandler(tornado.web.RequestHandler):
    async def post(self):
        pass


# SYSTEM HANDLERS. DO NOT TRY TO CHANGE THEM.

class SystemAddHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('system_add.html')

    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.adding_new_system_validator(data)):
            try:
                response = await asyncio.create_task(insert_system(system_id=data['system_id'], system_name=data['system_name'], system_type=data['system_type'], auth_data_fields=data['auth_data_fields']))
            except Exception as e:
                response = {
                    "status": "error", 
                    "message": str(e)
                }

            if response['status'] == 'success':
                success_message = response['message']
                try:
                    self.render("success.html", message=success_message)
                except Exception as e:
                    error_message = str(e)
                    self.render("error.html", message=error_message)
            else:
                error_message = response["message"]
                self.render("error.html", message=error_message)
        else:
            error_message = "Data is not valid. Please provide valid data!"
            self.render("error.html", message=error_message)

