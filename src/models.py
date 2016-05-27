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
import constants


logger = logging.getLogger(__name__)
class Session(object):
    """
    with Session() as session:
        session.query()

    """
    engine = create_engine("mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(**settings.mysql_config),
                           encoding='utf8',
                           connect_args=dict(connect_timeout=2), # don't change the timeout value
                           max_overflow=10,
                           poolclass=sqlalchemy.pool.QueuePool,
                           pool_size=32,
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

# test table
class TestModel(BaseModel):
    """
    TestModel.__table__.drop(bind=Sesion.engine)
    TestModel.__table__.create(bind=Sesion.engine)

    """
    __tablename__ = "tb_test"

    # 主键
    id = Column('id', INTEGER, autoincrement=True, primary_key=True)

    #
    name = Column('name', VARCHAR(100), nullable=False)

    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    pass
    

# 手机号码白名单
class PhoneWhiteListModel(BaseModel):
    '''phone white list'''
    __tablename__ = "tb_phone_white_list"
    # 主键
    id = Column('id', INTEGER, autoincrement=True, primary_key=True)

    #
    phone = Column('phone', CHAR(11), nullable=False, unique=True)

    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    pass

class UserModel(BaseModel):
    '''user'''
    __tablename__ = 'tb_user'
    # 
    id = Column('id', INTEGER, autoincrement=True, primary_key=True)

    # contact information
    phone = Column('phone', CHAR(11), nullable=False, unique=True)
    name = Column('name', VARCHAR(8), nullable=False, index=True)
    email = Column('email', VARCHAR(64), nullable=False, unique=True)
    company_name = Column('company_name', VARCHAR(128), nullable=False)
    company_url = Column('company_url', VARCHAR(128), nullable=False)

    #
    token = Column('token', CHAR(48), nullable=False, unique=True)
    key = Column('key', CHAR(32), nullable=False)

    #
    status = Column('status', Enum(constants.StatusEnum), nullable=False)
    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    pass


class AuthModel(BaseModel):
    __tablename__ = 'tb_auth'
    __table_args__ = ((UniqueConstraint('user_id', 'do', name='unique_user_id_do')),)
    #
    
    id = Column('id', INTEGER, autoincrement=True, primary_key=True)
    user_id = Column('user_id', INTEGER, index=True, nullable=False)
    do = Column('do', Enum(constants.AuthDoEnum), index=True, nullable=False)
    quota = Column('quota', INTEGER, default=0)
    
    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    
    pass
    


class PhoneCheckLogModel(BaseModel):
    __tablename__ = "tb_phone_check_log"
    #
    id = Column('id', INTEGER, autoincrement=True, primary_key=True)

    #
    user_id = Column('user_id', INTEGER, index=True, nullable=False)
    phone = Column('phone', CHAR(11), index=True, nullable=False)
    ip = Column('ip', VARCHAR(64), index=True, nullable=False)


    action = Column('action', Enum(constants.ActionEnum), index=True, nullable=False)
    # 
    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    pass

class PhoneCheckResultModel(BaseModel):
    __tablename__ = 'tb_phone_check_result'
    #
    id = Column('id', INTEGER, autoincrement=True, primary_key=True)

    #
    phone = Column('phone', CHAR(11), nullable=False, unique=True)
    rating = Column('rating', Enum(constants.RatingEnum), nullable=False, index=True)

    # 
    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    pass

