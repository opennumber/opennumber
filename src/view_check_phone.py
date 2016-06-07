# -*- coding: utf-8 -*
from _imports import *

#
import utils
import models
from models import PhoneCheckLogModel
from sqlalchemy import func, distinct

logger = logging.getLogger(__name__)

class PhoneCheckLogView(object):
    user_id_rank_map = utils.CountRankMap([(3, 1), (5, 2), (10, 4), (20, 20)])
    ip_rank_map = utils.CountRankMap([(3, 1), (5, 2), (10, 4), (20, 10)])
    
    @classmethod
    def get_user_id_rank(cls, phone):
        """
        查看该phone在多少个平台平台登录过
        """

        with models.Session() as session:
            day = datetime.date.today()
            model = PhoneCheckLogModel
            count = session.query(func.count(distinct(model.user_id))).filter(model.phone==phone, model.create_datetime>=day).first()[0]

            rank = cls.user_id_rank_map.get_rank(count)
            logger.debug("phone access user_id count: %s at %s, rank: %s", count, day, rank)
            return rank
        return


    @classmethod
    def get_ip_rank(cls, phone):
        with models.Session() as session:
            day = datetime.date.today()
            model = PhoneCheckLogModel
            count = session.query(func.count(distinct(model.ip))).filter(model.phone==phone, model.create_datetime>=day).first()[0]

            rank = cls.ip_rank_map.get_rank(count)
            logger.debug("phone access ip count: %s at %s, rank: %s", count, day, rank)
            return rank
        return


    pass

