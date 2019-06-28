#!/usr/bin/env python

import tornado.web
import tornado.ioloop
import tornado.options
from tornado.options import define
from handlers.mainHandler import MainHandler
from config.database import dbconfs

from database_mod import pkgrelease_engine

from sqlalchemy.orm import sessionmaker, scoped_session

# import pymysql
# pymysql.install_as_MySQLdb()

define("listen_port", default=80, help="server listen port", type=int, group="global")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        settings = dict(
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)
        self.db = {}
        self.db['pkgrelease'] = scoped_session(sessionmaker(bind=pkgrelease_engine,
                                              autocommit=False, autoflush=True,
                                              expire_on_commit=False))

if __name__ == "__main__":
    app = Application()
    tornado.options.parse_config_file("config/tornado.conf")
    app.listen(tornado.options.options['listen_port'])
    tornado.ioloop.IOLoop.current().start()
