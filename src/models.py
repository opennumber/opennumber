# -*- coding: utf-8 -*
from __future__ import absolute_import


from _imports import *


from sqlalchemy import *
import sqlalchemy.pool
import sqlalchemy.orm
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy_utils import Timestamp
from sqlalchemy.ext.declarative import declarative_base

#
import context
import settings

logger = logging.getLogger(__name__)

class Session(object):
    """
    """
    engine = create_engine("mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(**settings.mysql_config),
                           encoding='utf8',
                           max_overflow=10,
                           poolclass=sqlalchemy.pool.QueuePool,
                           pool_size=64,
                           pool_recycle=60*30, # half hour
                           pool_reset_on_return=None,
                           pool_timeout=1,
                           echo=False)



    session_template = sessionmaker(bind=engine, autocommit=True, autoflush=False)

    def __init__(self):
        session = scoped_session(type(self).session_template)
        self.session = session
        pass


    @classmethod
    def new(cls):
        session = cls()
        return  session#
    
    def __enter__(self):
        return  self.session# 

    def __exit__(self, _type, value, _traceback):
        if _type is None and value is None and _traceback is None:
            logger.debug("orm session exit success")
            self.session.flush()
            self.session.remove()
            self.session.close()
            del self.session
            return True
        else:
            logger.exception('')
            self.session.rollback()
            self.session.close()
            self.session.remove()
            del self.session
            return False

        return False
    pass


session = Session().session
BaseModel = declarative_base()

class TestModel(BaseModel):
    """
TestModel.__table__.drop(bind=Sesion.engine)
TestModel.__table__.create(bind=Sesion.engine)

    """
    __tablename__ = "test"

    # 主键
    id = Column('id', INTEGER, autoincrement=True, primary_key=True)

    #
    name = Column('name', VARCHAR(100), nullable=False)

    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    pass
    

if __name__ == "__main__":
    with Session() as session:
        session.add(TestModel(name="hahah"))
        session.flush()
        session.add(TestModel(name="haha"))
        
