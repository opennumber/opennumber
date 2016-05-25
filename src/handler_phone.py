# -*- coding: utf-8 -*
from _imports import *

#
import utils
import settings
import myweb


class CheckHandler(myweb.JsonHandler):
    def get(self):
        now = datetime.datetime.now()
        phone = self.get_argument_phone('phone')
        create_datetime = self.get_argument_datetime('create_datetime', now)

        ip = self.get_argument("ip", '')
        action = self.get_argument("action")

        return

    pass


class CommitWhileListHandler(myweb.JsonHandler):
    def get(self):
        phone = self.get_argument("phone")

        return
    pass


class CommitCheckResultHandler(myweb.JsonHandler):
    def get(self):
        phone = self.get_argument('phone')
        rating = self.get_argument("rating")

        return

    pass



