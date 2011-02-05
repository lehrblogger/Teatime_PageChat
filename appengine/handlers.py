import logging
import os
from django.utils import simplejson as json
import urllib

from google.appengine.ext import webapp
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app, login_required


from models import Conver, Message
import utils

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        convers = []
        messages = Message.all().filter('author =', user).fetch(1000)
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
        logging.warning(text)
        if text:
            conver_url = self.request.get('url')
            conver_url = utils.unescape(conver_url)
            conver = Conver.all().filter('url =', conver_url).get()
            if not conver:
                conver = Conver(url=conver_url)
                conver.put()
            logging.warning(users.get_current_user())    
            logging.warning(text)
            logging.warning(conver)
            message = Message(author=users.get_current_user(), text=text, conver=conver)
            message.put()
            # self.distribute_message(message)
            
        else:
            logging.error("No message '%S'saved for %s", text, conver_url)


class ConverPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        conver_url = self.request.get('url')
        if not conver_url:
            self.response.out.write('No such conversation')
            return
        conver_url = utils.unescape(conver_url)
        conver = Conver.all().filter('url =', conver_url).get()
        messages = Message.all().filter('conver =', conver).order('created').fetch(1000)
    
        self.response.out.write(template.render(
            os.path.join(os.path.dirname(__file__),
            'templates/conver.html'), 
            {
                'conver_url': conver_url,
                'messages': messages,
                'loginorout_text': 'Log out',
                'loginorout_url': users.create_logout_url(self.request.uri)
            }
        ))
        # 
        # template_values = {'conver_url': conver_url,
        #                    'messages': messages,
        #                   }
        # os_path = os.path.dirname(__file__)
        # self.response.out.write(template.render(os.path.join(os_path, 'templates/conver.html'), template_values))

    # 
    # self.response.out.write(template.render(path, template_values))
    # 
    #     game_key = user.user_id()
    #     game = Game(key_name = game_key,
    #                 userX = user,
    #                 moveX = True,
    #                 board = '         ')
    #     game.put()
    #   else:
    #     game = Game.get_by_key_name(game_key)
    #     if not game.userO:
    #       game.userO = user
    #       game.put()
    # 
    #   game_link = 'http://localhost:8080/?g=' + game_key
    # 
    #   if game:
    #     token = channel.create_channel(user.user_id() + game_key)
    #     template_values = {'token': token,
    #                        'me': user.user_id(),
    #                        'game_key': game_key,
    #                        'game_link': game_link,
    #                        'initial_message': GameUpdater(game).get_game_message()
    #                       }
    #     path = os.path.join(os.path.dirname(__file__), 'index.html')
    # 
    #     self.response.out.write(template.render(path, template_values))
    #   else:
    #     self.response.out.write('No such game')
 


application = webapp.WSGIApplication([
    ('/download', DownloadPage),
    ('/message', MessageHandler),
    ('/conver', ConverPage),
    ('/', MainPage)], debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
