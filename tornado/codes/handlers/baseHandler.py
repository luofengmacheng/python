#!/usr/bin/env python

import tornado.web

class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db
        
