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
import utils
import err

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
    status = Column('status', Enum(*[e.value for e in constants.StatusEnum]), nullable=False)
    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    pass


class UserAuthModel(BaseModel):
    __tablename__ = 'tb_user_auth'
    __table_args__ = ((UniqueConstraint('user_id', 'auth', name='unique_user_id_do')),)
    #
    
    id = Column('id', INTEGER, autoincrement=True, primary_key=True)
    user_id = Column('user_id', INTEGER, index=True, nullable=False)
    auth = Column('auth', Enum(*[e.value for e in constants.AuthEnum]), index=True, nullable=False)
    quota = Column('quota', INTEGER, default=0)
    
    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    
    pass
    

class UserAuthQuotaRedis(object):
    """
    把用户每天的访问次数放在redis中，每访问一次加1
    """
    pattern = 'user_auth_quota:{user_id}:{auth}'

    def __init__(self, user_id, auth, quota):
        assert auth in constants.AuthEnum.__members__, 'invali user_auth: "%s"' % (user_auth,)
        assert isinstance(quota, utils.IntegerTypes), 'invalid quota value, "%s"' % (quota,)
        
        self.redis_key = self.pattern.format(user_id=user_id, auth=auth)
        self.quota = quota
        pass

    def access(self):
        #
        used_count = context.redis_client.incr(self.redis_key)
        logger.debug("key: %s, used: %s", self.redis_key, used_count)        
        if used_count > self.quota:
            raise err.QuotaOverFlow(self.quota)


        # 
        if used_count == 1:
            ttl = utils.get_today_countdown_seconds()
            context.redis_client.expire(self.redis_key, ttl)
            logger.info('set key expire: key: %s, ttl: %s', self.redis_key, ttl)
            pass
        
        return used_count
    
    def flush(self):
        context.redis_client.delete(self.redis_key)
        logger.info("flush key: %s", self.redis_key)
        return

    pass
        

class PhoneCheckLogModel(BaseModel):
    __tablename__ = "tb_phone_check_log"
    #
    id = Column('id', INTEGER, autoincrement=True, primary_key=True)

    #
    user_id = Column('user_id', INTEGER, index=True, nullable=False)
    phone = Column('phone', CHAR(11), index=True, nullable=False)
    ip = Column('ip', VARCHAR(64), index=True, nullable=False)


    action = Column('action', Enum(*[e.value for e in constants.ActionEnum]), index=True, nullable=False)
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
    rating = Column('rating', Enum(*[e.value for e in constants.RatingEnum]), nullable=False, index=True)

    # 
    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    pass


def create_table(table_name):
    model = globals()[table_name]
    pass


if __name__ == "__main__":
    BaseModel.metadata.drop_all(bind=Session.engine, checkfirst=True)        
    BaseModel.metadata.create_all(bind=Session.engine, checkfirst=True)
    
    #UserModel.__table__.create(bind=Session.engine, checkfirst=False)
