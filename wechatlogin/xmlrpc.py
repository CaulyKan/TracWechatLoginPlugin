# -*- coding: utf8 -*-
#
# Copyright (C) Cauly Kan, mail: cauliflower.kan@gmail.com
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from trac.core import Component, implements
from tracrpc.api import IXMLRPCHandler
from xmlrpclib import ServerProxy


class WechatLoginRPC(Component):
    implements(IXMLRPCHandler)

    def __init__(self):
        pass

    def xmlrpc_namespace(self):
        return 'wechat'

    def xmlrpc_methods(self):
        yield (None, ((bool, str, str, str),), self.register)
        yield (None, ((list, str),), self.login)

    def register(self, req, openid, user, passwd):
        try:
            with self.env.db_transaction as db:
                self._check_login(req, user, passwd)
                cursor = db.cursor()
                cursor.execute('INSERT INTO wechat(openid, user, passwd) VALUES (%s, %s, %s)', [openid, user, passwd])
                return True
        except Exception as e:
            print e
            return False

    def login(self, req, openid):
        with self.env.db_query as db:
            cursor = db.cursor()
            cursor.execute('SELECT user, passwd FROM wechat WHERE openid = %s', [openid])
            row = cursor.fetchone()
            try:
                user, passwd = row[0], row[1]
                self._check_login(req, user, passwd)
                return [user, passwd]
            except:
                return []

    def _check_login(self, req, user, passwd):

        p = ServerProxy('http://%s:%s@localhost:%s/login/rpc' % (user, passwd, req.server_port))
        p.system.getAPIVersion()
