#!/usr/bin/env python

import tornado.web
from .baseHandler import BaseHandler
import models.database_mod

class MainHandler(BaseHandler):

   def get(self):
       self.write("It works!")
