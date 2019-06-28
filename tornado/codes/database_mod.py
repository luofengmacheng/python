#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from config.database import dbconfs

# 使用mysql数据库需要安装
# 1 mysql客户端：pip install mysql
# 2 mysql库：pip install pymysql
pkgrelease_engine = create_engine('mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}?charset=utf8'.format(**dbconfs['t_pkgrelease']),
                                  encoding='utf-8', echo=False, pool_size=100, pool_recycle=10)

pkgrelease_Base = declarative_base(pkgrelease_engine)


