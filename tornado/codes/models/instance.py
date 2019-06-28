#!/usr/bin/env python

from database_mod import pkgrelease_Base
from sqlalchemy import Column,Integer,VARCHAR, String,DateTime,Boolean

class Instance(pkgrelease_Base):
    __tablename__ = 'sPackage'
    packageId = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255))
