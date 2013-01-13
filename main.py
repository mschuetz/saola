#!/usr/bin/env python

import webapp2
from google.appengine.api import xmpp
from google.appengine.ext import db
from google.appengine.api import users


class NotificationReceiver(db.Model):
  name = db.StringProperty(required=True)
  jid = db.StringProperty(required=True)

class InviteHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.response.write("Welcome, %s! I'll send you an XMPP invite" % (user.nickname(),))
            xmpp.send_invite(user.email())
            recv = NotificationReceiver(name=user.nickname(), jid=user.email())
            recv.put()
        else:
            self.response.write("<a href=\"%s\">Sign in or register</a>." % users.create_login_url("/"))

class MonitorHandler(webapp2.RequestHandler):
    def get(self, site):
        self.response.write('monitoring .. ' + site)

class ReceiversHandler(webapp2.RequestHandler):
    def get(self):
        for receiver in db.GqlQuery("SELECT jid FROM NotificationReceiver"):
            self.response.write('receiver: ' + receiver.jid)
 
class XMPPHandler(webapp2.RequestHandler):
    def get(self):
        res = xmpp.send_message('mschuetz@gmail.com', 'hello there')
        msg = 'no match'
        if res == xmpp.NO_ERROR:
            msg = 'no error'
        elif res == xmpp.INVALID_JID:
            msg = 'invalid jid'
        elif res == xmpp.OTHER_ERROR:
            msg = "other_error"
        
        self.response.write('sent message: ' + msg)

app = webapp2.WSGIApplication([('/asdf', XMPPHandler), ('/invite', InviteHandler),
                               webapp2.Route('/monitor/<site>', MonitorHandler),
                               ('/receivers', ReceiversHandler)],
                              debug=True)
