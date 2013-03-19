#!/usr/bin/env python

import webapp2
import re
import logging
import string
import time
import sys
from google.appengine.api import xmpp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api.urlfetch import fetch

USERS = ('mschuetz@gmail.com',)

class NotificationReceiver(db.Model):
    jid = db.StringProperty(required=True)

class InviteHandler(webapp2.RequestHandler):
    def post(self):
        jid = self.request.get('jid')
        self.response.write("Welcome, %s! I'll send you an XMPP invite" % jid)
        xmpp.send_invite(jid)
        recv = NotificationReceiver(jid=jid)
        recv.put()

def notify_all(msg, *args):
    for user in db.GqlQuery("select * from NotificationReceiver"):
        xmpp.send_message(user.jid, msg % args)

class MonitorHandler(webapp2.RequestHandler):
    def get(self):
        for site in db.GqlQuery("select * from MonitorSubject"):
            try:
                url = '%s?%s' % (site.url, time.time())
                logging.info('fetching %s', url)
                res = fetch(url)
                if res.status_code != 200:
                    notify_all('fetch(%s):\nstatus %s', site.url, res.status_code)
            except:
                notify_all('fetch(%s):\nraised exception %s', site.url, sys.exc_info()[0])

class MonitorSubject(db.Model):
    url = db.StringProperty(required=True)

def add_url(url):
    MonitorSubject(url=url).put()
    return 'ok'

def remove_url(url):
    db.GqlQuery('delete from MonitorSubject where url=%s' % url)
    return 'ok'

def list_urls():
    return string.join([site.url for site in db.GqlQuery('select * from MonitorSubject')], '\n')

MSG_HANDLERS = { '^add (.*)$': add_url, '^rm (.*)$': remove_url, '^list': list_urls, '^ping': lambda : 'pong'}

class MessageHandler(webapp2.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        logging.info("message from %s", message.sender)
        jid_without_resource = re.match('^(.*@.*)/.*$', message.sender).group(1)
        if jid_without_resource not in USERS:
            message.reply('you\'re not authorized to use this service')
            raise Exception('message from unauthorized sender')
        msg = message.body.lower()
        
        for regex, handler in MSG_HANDLERS.iteritems():
            match = re.match(regex, msg)
            if match:
                message.reply(handler(*match.groups()))
            

app = webapp2.WSGIApplication([('/_ah/xmpp/message/chat/', MessageHandler),
                               ('/monitor', MonitorHandler), ('/invite', InviteHandler)],
                              debug=True)
