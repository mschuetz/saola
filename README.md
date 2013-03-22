# Saola
A minimalistic web site monitoring tool for Google App Engine.
[![Build Status](https://secure.travis-ci.org/mschuetz/saola.png)](http://travis-ci.org/mschuetz/saola)

## Setup
Register a (free) GAE application, let's say you call it <MYAPP>.

	git clone https://github.com/mschuetz/saola.git
	cd saola
	sed -i bak -e s/INSERT_APP_NAME/<MYAPP>/ app.yaml
	appcfg.py update .

Open (as the application administrator) https://<MYAPP>.appsport.com/s/index.html in your browser, enter your Jabber account (JID). The application will send you an XMPP invite (i.e. add you to their contact list). From now on you'll be able to control it via Jabber messages. You can add multiple Jabber accounts through this form. 

## Jabber message command reference
###	ping
Will respond with pong, if you've previously added your JID to the list of users.

### add HTTP_URL
Adds the given URL to the list of monitoring subjects. You will receive alerts every time the URL cannot be fetched. The actual URL that will be fetched will have a query paramerter appended to circumvent the caching mechanism of the GAE urlfetch library.

### rm HTTP_URL
Stop monitoring the URL.

### list
Lists all URLs that are currently monitored and have been added by the sender.

## Caveats/TODO
* Add monitoring tasks to a queue instead of directly fetching them in the cron callback
* Intelligent alerts, i.e. if a problem persists, reduce the alerting frequency.
* Instead of appending the current time as a query parameter, evaluate using a Cache-Control header to circumvent the urlfetch cache.

## MIT License

Copyright (c) 2013 Matthias Schütz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
