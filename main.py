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

class User(db.Model):
    jid = db.StringProperty(required=True)

class InviteHandler(webapp2.RequestHandler):
    def post(self):
        jid = self.request.get('jid')
        self.response.write("Welcome, %s! I'll send you an XMPP invite" % jid)
        xmpp.send_invite(jid)
        recv = User(jid=jid)
        recv.put()

def all_users():
    return db.GqlQuery("select * from User")

def multi_message(jids, msg, *args):
    for jid in jids:
        xmpp.send_message(jid, msg % args)

class MonitorHandler(webapp2.RequestHandler):
    def get(self):
        sites = {}
        for site in db.GqlQuery("select * from MonitorSubject"):
            notified_jids = sites.get(site.url, [])
            notified_jids.append(site.jid)
            sites[site.url] = notified_jids
        
        for url, notified_jids in sites.iteritems():
            try:
                unique_url = '%s?%s' % (url, time.time())
                logging.info('fetching %s', unique_url)
                res = fetch(unique_url)
                if res.status_code != 200:
                    multi_message(notified_jids, 'fetch(%s):\nstatus %s', url, res.status_code)
            except:
                multi_message(notified_jids, 'fetch(%s):\nraised exception %s', url, sys.exc_info()[0])

class MonitorSubject(db.Model):
    url = db.StringProperty(required=True)
    jid = db.StringProperty(required=True)

def add_url(sender, url):
    MonitorSubject(url=url, jid=sender).put()
    return 'ok'

def remove_url(sender, url):
    for site in db.GqlQuery('select * from MonitorSubject where url=:1 and jid=:2', url, sender):
        site.delete()
    return 'ok'

def list_urls(sender):
    return string.join([site.url for site in db.GqlQuery('select * from MonitorSubject where jid=:1', sender)], '\n')

MSG_HANDLERS = { '^add (.*)$': add_url, '^rm (.*)$': remove_url, '^list': list_urls, '^ping': lambda _ : 'pong'}

def jid_without_resource(jid):
    return re.match('^(.*@.*)/.*$', jid).group(1)

class MessageHandler(webapp2.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        logging.info("message from %s", message.sender)
        if jid_without_resource(message.sender) not in [user.jid for user in all_users()]:
            message.reply('you\'re not authorized to use this service')
            raise Exception('message from unauthorized sender')
        
        for regex, handler in MSG_HANDLERS.iteritems():
            match = re.match(regex, message.body, re.IGNORECASE)
            if match:
                message.reply(handler(jid_without_resource(message.sender), *match.groups()))


app = webapp2.WSGIApplication([('/_ah/xmpp/message/chat/', MessageHandler),
                               ('/monitor', MonitorHandler), ('/invite', InviteHandler)],
                              debug=True)
