import logging
from google.appengine.ext import db
from google.appengine.api import users


class PermaUser(db.Model):
    user = db.UserProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    
    def user_id(self):
        return self.user.user_id()
        
    def display_name(self):
        return self.user.nickname()
        
    def get_current_permauser():
        user = users.get_current_user()
        permauser = PermaUser.all().filter('user = ', user).get()
        if not permauser:
            permauser = PermaUser(user=user)
            permauser.put()
        return permauser
    get_current_permauser = staticmethod(get_current_permauser)
    
    
class Conver(db.Model):
    url = db.LinkProperty()
    watchers = db.ListProperty(db.Key, default=[])
    created = db.DateTimeProperty(auto_now_add=True)
    
    def add_watcher(self, permauser):
        self.watchers.append(permauser.key())
    
    def remove_watcher(self, permauser):
        self.watchers.remove(permauser.key())
        
    def get_watchers(self):
        return [db.get(watcher) for watcher in self.watchers]

    def get_for_url(conver_url):
        conver = Conver.all().filter('url =', conver_url).get()
        if not conver:
            conver = Conver(url=conver_url)
            conver.put()
        return conver
    get_for_url = staticmethod(get_for_url)



class Message(db.Model):
    author = db.ReferenceProperty(PermaUser)
    text = db.StringProperty(multiline=True)
    conver = db.ReferenceProperty(Conver)
    created = db.DateTimeProperty(auto_now_add=True)
