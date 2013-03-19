#!/usr/bin/env python

import webapp2
import re
import logging
from google.appengine.api import xmpp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api.urlfetch import fetch

USERS = ('mschuetz@gmail.com',)

class NotificationReceiver(db.Model):
  name = db.StringProperty(required=True)
  jid = db.StringProperty(required=True)

class InviteHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            self.response.write("Welcome, %s! I'll send you an XMPP invite" % (user.nickname(),))
            xmpp.send_invite(user.email())
            recv = NotificationReceiver(name=user.nickname(), jid=user.email())
            recv.put()
        else:
            self.response.write("<a href=\"%s\">Sign in or register</a>." % users.create_login_url("/"))

def notify_all(msg, *args):
    for user in USERS:
        xmpp.send_message(user, msg % args)

class MonitorHandler(webapp2.RequestHandler):
    def get(self):
        for site in db.GqlQuery("select url from MonitorSubject"):
            try: 
                res = fetch(site.url)
                if res.status_code != 200:
                    notify_all('fetch(%s):\nstatus %s', site.url, res.status_code)
            except e:
                notify_all('fetch(%s):\nraised exception %s', site.url, e)

class MonitorSubject(db.Model):
    url = db.StringProperty(required=True)

def add_url(url):
    MonitorSubject(url=url).put()
    'ok'

def remove_url(url):
    db.GqlQuery('delete from MonitorSubject where url=%s' % url)
    'ok'

def list_urls():
    string.join([site.url for site in db.GqlQuery('select from MonitorSubject')], '\n')

MSG_HANDLERS = {'^add (.*)$', add_url, '^rm (.*)$', remove_url, '^list', list_urls, '^ping', lambda : 'pong'}

class MessageHandler(webapp2.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        logging.info("message from %s", message.sender)
        jid_without_resource = re.match('^(.*@.*)/.*$', message.sender).group(1)
        if jid_without_resource not in USERS:
            message.reply('you\'re not authorized to use this service')
            raise Exception('message from unauthorized sender')
        msg = message.body.lower()
        
        if msg == 'ping':
            message.reply('pong')
        for regex, handler in MSG_HANDLERS:
            match = re.match(regex, msg)
            if match:
                message.reply(handler(*match.groups()))
            

app = webapp2.WSGIApplication([('/_ah/xmpp/message/chat/', MessageHandler),
                               ('/monitor', MonitorHandler), ('/invite', InviteHandler)],
                              debug=True)
