#!/usr/bin/env python

from .database_mod import pkgrelease_Base
from sqlalchemy import Column,Integer,VARCHAR, String,DateTime,Boolean

class Instance(pkgrelease_Base):
    __tablename__ = 'sInstances'
    ip = Column(VARCHAR(64))
    name = Column(VARCHAR(255))
