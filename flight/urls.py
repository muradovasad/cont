import tornado.web

from .handlers import SearchHandler
from .handlers import OfferHandler
from .handlers import UpsellHandler
from .handlers import RulesHandler
from .handlers import BookingHandler
from .handlers import TicketingHandler

from .handlers import SystemAddHandler

def make_app():
    app_urls = tornado.web.Application([
        (r"/search/", SearchHandler),
        (r"/offers/", OfferHandler),
        (r"/upsell/", UpsellHandler),
        (r"/rules/",  RulesHandler),
        (r"/booking/", BookingHandler),
        (r"/ticketing/", TicketingHandler),

        (r"/add-new-system/", SystemAddHandler)
    ],
    debug=False,
    autoreload=True,
    template_path="flight/templates")

    return app_urls
