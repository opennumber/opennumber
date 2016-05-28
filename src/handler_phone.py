# -*- coding: utf-8 -*
from _imports import *

import web
#
import utils
import settings
import myweb
import constants
import models

class CheckHandler(myweb.JsonHandler):
    def get(self):
        phone = self.get_argument_phone('phone')
        
        self.check(constants.AuthEnum.phone_check, [phone, ])
        
        now = datetime.datetime.now()
        create_datetime = self.get_argument_datetime('create_datetime', now)

        ip = self.get_argument_ip("ip", '')
        action = self.get_argument_action("action")

        session = web.ctx.orm
        # add check log
        check_log = models.PhoneCheckLogModel(user_id=web.ctx.user.id,
                                              phone=phone,
                                              ip=ip,
                                              action=action)
        session.add(check_log)

        # check in whitelist
        result = dict(rating=constants.RatingEnum.green.value)
        if session.query(models.PhoneWhiteListModel).filter_by(phone=phone).scalar():
            result['rating'] = constants.Rating.white.value
            return result

        # check in check result
        check_result = session.query(models.PhoneCheckResultModel).filter_by(phone=phone).scalar()
        if check_result:
            result['rating'] = check_result.rating
            return result

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

