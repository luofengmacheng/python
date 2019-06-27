#!/usr/bin/env python

import tornado.web
import tornado.ioloop
import tornado.options
from tornado.options import define
from handlers.mainHandler import MainHandler
from config.database import dbconfs

define("listen_port", default=80, help="server listen port", type=int, group="global")

import pymysql
pymysql.install_as_MySQLdb()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        settings = dict(
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

if __name__ == "__main__":
    app = Application()
    tornado.options.parse_config_file("config/tornado.conf")
    app.listen(tornado.options.options['listen_port'])
    tornado.ioloop.IOLoop.current().start()
