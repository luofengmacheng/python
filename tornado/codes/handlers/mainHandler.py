#!/usr/bin/env python

import tornado.web
from .baseHandler import BaseHandler

from models.instance import Instance

class MainHandler(BaseHandler):

   def get(self):
       data = self.db['pkgrelease'].query(Instance).all()
       print(data)
       self.write("query ok")
