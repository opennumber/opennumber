# -*- coding: utf-8 -*
from __future__ import absolute_import


from _imports import *
import pymysql
#import sqlalchemy as sa
from sqlalchemy import *
from sqlalchemy.dialects.mysql import BIGINT
import sqlalchemy.pool
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import EncryptedType
import ipaddress


#
import context
import settings
import constants
import utils
import err

logger = logging.getLogger(__name__)
sqlalchemy_encrypt_key = settings.sqlalchemy_encrypt_key
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
                              pool_recycle=60*10, # half hour
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
            if not isinstance(_type, pymysql.err.IntegrityError):
                logger.exception('')
            self.session.rollback()
            self.session.remove()            
            self.session.close()
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
    id = Column('id', BIGINT(unsigned=True), autoincrement=True, primary_key=True)

    #
    name = Column('name', VARCHAR(100), nullable=False)

    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    pass
    


class UserModel(BaseModel):
    '''user'''
    __tablename__ = 'tb_user'
    # 
    id = Column('id', BIGINT(unsigned=True), autoincrement=True, primary_key=True)

    # contact information
    phone = Column('phone', CHAR(11), nullable=False, unique=True)
    name = Column(EncryptedType(Unicode, sqlalchemy_encrypt_key), nullable=False)
    email = Column(VARCHAR(64), nullable=False, unique=True)
    company_name = Column(EncryptedType(Unicode, sqlalchemy_encrypt_key), nullable=False)
    company_url = Column(EncryptedType(Unicode, sqlalchemy_encrypt_key), nullable=False)

    #
    token = Column('token', VARCHAR(64), nullable=False, unique=True)
    key = Column('key', EncryptedType(Unicode, sqlalchemy_encrypt_key), nullable=False)

    #
    status = Column('status', Enum(*[e.value for e in constants.StatusEnum]), nullable=False, default='1')
    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    #
    @classmethod
    def create(cls, name, phone, email, company_name, company_url, token=None, key=None):
        global session
        if not token:
            token = utils.get_unique_string()
            pass

        if not key:
            key = utils.generate_random_string(24)
            pass

        user = cls()
        user.name = name
        user.phone = phone
        user.email = email
        user.company_name = company_name
        user.company_url = company_url
        user.token = token
        user.key = key
        user.status = constants.StatusEnum.valid.value

        #
        session.add(user)
        session.flush()
        new_user = session.query(cls).filter_by(token=token).one()

        logger.warn('create user. user.phone: %s, user.id: %s, user.key: %s, user.token: %s',
                    new_user.phone, new_user.id, user.key, user.token)
        return new_user
    pass


class UserAuthModel(BaseModel):
    __tablename__ = 'tb_user_auth'
    __table_args__ = ((UniqueConstraint('user_id', 'auth', name='unique_user_id_do')),)
    #
    
    id = Column('id', BIGINT(unsigned=True), autoincrement=True, primary_key=True)
    user_id = Column('user_id', BIGINT(unsigned=True), index=True, nullable=False)
    auth = Column('auth', Enum(*[e.value for e in constants.AuthEnum]), index=True, nullable=False)
    quota = Column('quota', BIGINT(unsigned=True), default=0)
    
    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)


    @classmethod
    def create(cls, user_id, auth, quota=200):
        global session
        user = session.query(UserModel).get(user_id)

        user_auth = cls(user_id=user_id, auth=auth, quota=quota)

        session.add(user_auth)
        session.flush()

        #
        new_user_auth = session.query(cls).filter_by(user_id=user_id, auth=auth).one()
        
        logger.info("create user quota. user_id: %s, auth: %s, id: %s, quota: %d",
                    user_id, auth, new_user_auth.id, quota)
        return new_user_auth

    pass
    

class UserAuthQuotaRedis(object):
    """
    把用户每天的访问次数放在redis中，每访问一次加1
    """
    pattern = 'user_auth_quota:{user_id}:{auth}'

    def __init__(self, user_id, auth, quota):
        assert hasattr(constants.AuthEnum, auth), 'invali user_auth: "%s"' % (auth,)
        assert isinstance(quota, utils.IntegerTypes), 'invalid quota value, "%s"' % (quota,)
        
        self.redis_key = self.pattern.format(user_id=user_id, auth=auth)
        self.quota = quota
        pass

    def access(self):
        #
        used_count = context.redis_client.incr(self.redis_key)
        logger.debug("key: %s, used: %s, quota: %s", self.redis_key, used_count, self.quota)
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
        

# 手机号码白名单
class PhoneWhiteListModel(BaseModel):
    '''phone white list'''
    __tablename__ = "tb_phone_white_list"
    # 主键
    id = Column('id', BIGINT(unsigned=True), autoincrement=True, primary_key=True)

    #
    user_id = Column(BIGINT(unsigned=True), nullable=False, index=True)
    phone = Column('phone', CHAR(11), nullable=False, unique=True)

    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    
    pass


class PhoneCheckLogModel(BaseModel):
    __tablename__ = "tb_phone_check_log"
    #
    id = Column('id', BIGINT(unsigned=True), autoincrement=True, primary_key=True)

    #
    user_id = Column('user_id', BIGINT(unsigned=True), index=True, nullable=False)
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
    id = Column('id', BIGINT(unsigned=True), autoincrement=True, primary_key=True)

    #
    user_id = Column(BIGINT(unsigned=True), index=True, nullable=False)
    
    phone = Column('phone', CHAR(11), nullable=False, unique=True)
    rating = Column('rating', Enum(*[e.value for e in constants.RatingEnum]), nullable=False, index=True)

    # 
    create_datetime = Column('create_datetime', DATETIME, index=True, nullable=False, default=datetime.datetime.now)
    update_datetime = Column('update_datetime', DATETIME, index=True, nullable=False, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    
    @classmethod
    def create(cls, user_id, phone, rating):
        global session
        if not hasattr(constants.RatingEnum, rating):
            raise err.InvalidRating()

        if not constants.phone_number_regex.match(phone):
            raise err.InvalidPhoneNumber()
        

        result = session.query(PhoneCheckResultModel).filter_by(phone=phone).scalar()

        # insert new
        if not result:
            n = cls()
            n.user_id = user_id
            n.phone = phone
            n.rating = rating
            session.add(n)
            session.flush()
            logger.info('insert phone_check_result. user_id: %s, phone: %s, rating: %s',
                        user_id, phone, rating)
            return n

        # update
        if constants.RatingEnum.greater_than(rating, result.rating):
            result.rating = rating
            session.flush()
            logger.info('update phone_check_result. user_id: %s, phone: %s, rating: %s',
                        user_id, phone, rating)

            return result

        return result
                
    pass



if __name__ == "__main__":
    #BaseModel.metadata.drop_all(bind=Session.engine, checkfirst=True)        
    #BaseModel.metadata.create_all(bind=Session.engine, checkfirst=True)
    
    #UserModel.__table__.drop(bind=Session.engine, checkfirst=True)
    #UserModel.__table__.create(bind=Session.engine, checkfirst=True)    
    pass
