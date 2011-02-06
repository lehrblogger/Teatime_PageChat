import logging
import os
from django.utils import simplejson as json
import urllib

from google.appengine.ext import webapp
from google.appengine.api import channel
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app, login_required
from google.appengine.api import users # for logout url


from models import Conver, Message, PermaUser
import utils

class MainPage(webapp.RequestHandler):
    def get(self):
        permauser = PermaUser.get_current_permauser()
        convers = []
        messages = Message.all().filter('author =', permauser).fetch(1000)
        for message in messages:
            conver.append(message.conver.url)
        self.response.out.write(template.render(
            os.path.join(os.path.dirname(__file__),
            'templates/home.html'), 
            {
                'convers': convers,
                'loginorout_text': 'Log out',
                'loginorout_url': users.create_logout_url(self.request.uri)
            }
        ))


class DownloadPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render(
            os.path.join(os.path.dirname(__file__),
            'templates/download.html'),
            {
                'loginorout_text': 'Log out',
                'loginorout_url': users.create_logout_url(self.request.uri)
            }
        ))



class MessageHandler(webapp.RequestHandler):
    def post(self):
        text = self.request.get('text')
        if text:
            conver_url = self.request.get('url')
            conver_url = utils.unescape(conver_url)
            conver = Conver.all().filter('url =', conver_url).get()
            if not conver:
                conver = Conver(url=conver_url)
                conver.put()
            message = Message(author=PermaUser.get_current_permauser(), text=text, conver=conver)
            message.put()
            self.distribute_message(message)
            
        else:
            logging.error("No message '%S'saved for %s", text, conver_url)

    def distribute_message(self, message):
        message_json = json.dumps({
            'author': message.author.display_name(),
            'message': message.text       
        })
        related_messages = Message.all().filter('conver =', message.conver).fetch(1000)
        participating_permausers = [message.author for message in related_messages]
        participating_permausers.extend(message.conver.get_watchers())
        pp_ids = [pp.user_id() for pp in participating_permausers]
        pp_ids = list(set(pp_ids))
        for pp_id in pp_ids:
            # ugly, but for now everyone can just get the messages
            channel.send_message(pp_id + str(message.conver.key().id_or_name()), message_json)


class OpenedHandler(webapp.RequestHandler):
    def post(self):
        conver_url = utils.unescape(self.request.get('url'))
        conver = Conver.all().filter('url =', conver_url).get()
        if not conver:
            conver = Conver(url=conver_url)
        permauser = PermaUser.get_current_permauser()
        conver.add_watcher(permauser)
        conver.put()


class ClosedHandler(webapp.RequestHandler):
    def post(self):
          conver_url = utils.unescape(self.request.get('url'))
          conver = Conver.all().filter('url =', conver_url).get()
          if conver:
              conver.remove_watcher(permauser) # or maybe we want to keep all watchers forever, so people get notified about what they looked at
              conver.put()
    

class ConverPage(webapp.RequestHandler):
    def get(self):
        permauser = PermaUser.get_current_permauser()
        conver_url = utils.unescape(self.request.get('url'))
        conver = Conver.all().filter('url =', conver_url).get()
        if not conver:
            conver = Conver(url=conver_url)
            conver.put() 
        messages = Message.all().filter('conver =', conver).order('created').fetch(1000)
        self.response.out.write(template.render(
            os.path.join(os.path.dirname(__file__),
            'templates/conver.html'), 
            {
                'token': channel.create_channel(permauser.user_id() + str(conver.key().id_or_name())),
                'conver_url': conver_url,
                'messages': [ {'author': message.author.display_name(), 'text': message.text} for message in messages],
                'loginorout_text': 'Log out',
                'loginorout_url': users.create_logout_url(self.request.uri)
            }
        ))

application = webapp.WSGIApplication([
    ('/download', DownloadPage),
    ('/message', MessageHandler),
    ('/opened', OpenedHandler),
    ('/closed', ClosedHandler),
    ('/conver', ConverPage),
    ('/', MainPage)], debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
