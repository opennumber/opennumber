# -*- coding: utf-8 -*
from _imports import *

import web
#
import utils
import settings
import myweb
import constants
import models

from models import PhoneWhiteListModel, PhoneCheckResultModel
from view_check_phone import PhoneCheckLogView

logger = logging.getLogger(__name__)
class CheckHandler(myweb.JsonHandler):
    count_rank = utils.CountRankMap([(10, 'green'), (15, 'yellow'), (25, 'red'), (35, "black")])
    
    def get(self):
        phone = self.get_argument_phone('phone')
        
        self.check(constants.AuthEnum.phone_check, [phone, ])
        
        now = datetime.datetime.now()
        create_datetime = self.get_argument_datetime('create_datetime', now)

        ip = self.get_argument_ip("ip", '')
        action = self.get_argument_action("action")
        user_id = web.ctx.user.id
        session = web.ctx.orm

        # add check log
        check_log = models.PhoneCheckLogModel(user_id=user_id,
                                              phone=phone,
                                              ip=ip,
                                              action=action,
                                              create_datetime=create_datetime)
        session.add(check_log)
        # check in whitelist
        result = dict(rating=constants.RatingEnum.green.value)
        if session.query(models.PhoneWhiteListModel).filter_by(phone=phone).scalar():
            result['rating'] = constants.Rating.white.value
            return result

        #
        ip_rank = PhoneCheckLogView.get_ip_rank(phone)
        user_id_rank = PhoneCheckLogView.get_user_id_rank(phone)

        rank = ip_rank * user_id_rank

        check_result = session.query(PhoneCheckResultModel).filter_by(phone=phone).scalar()
        if check_result:
            _rank = filter(lambda x: x[1]==check_result.rating, self.count_rank.count_rank_sorted_list)[0][0]
            rank = max(_rank, rank)
            pass
        
        result['rating'] = self.count_rank.get_rank(rank)
        logger.info('new rating: phone: %s, user_id: %s, rating: %s, rank: %s',
                    phone, user_id, result['rating'], rank)
        # 
        models.PhoneCheckResultModel.create(user_id, phone, result['rating'])
        
        return result

    pass


class CommitWhiteListHandler(myweb.JsonHandler):
    def get(self):
        phone = self.get_argument("phone")

        self.check(auth=constants.AuthEnum.phone_commit_white_list, sign_parameter_list=[phone,])

        session = web.ctx.orm
        if session.query(models.PhoneWhiteListModel).filter_by(phone=phone).scalar():
            return None
        else:
            white_list = models.PhoneWhiteListModel(user_id=web.ctx.user.id, phone=phone)
            session.add(white_list)
            session.flush()
            return None
        
        return None
    pass

class CommitCheckResultHandler(myweb.JsonHandler):
    def get(self):
        phone = self.get_argument("phone")
        self.check(auth=constants.AuthEnum.phone_commit_check_result, sign_parameter_list=[phone])

        rating = self.get_argument_rating('rating')
        session = web.ctx.orm
        user = web.ctx.user

        models.PhoneCheckResultModel.create(user_id=user.id, phone=phone, rating=rating)
        
        return 
                
