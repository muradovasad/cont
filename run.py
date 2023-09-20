import tornado.ioloop

from flight.models import create_database
import flight.urls as application

if __name__ == '__main__':
    create_database()
    app = application.make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()