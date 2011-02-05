from google.appengine.ext import db

class Conver(db.Model):
    url = db.StringProperty()

class Message(db.Model):
    author = db.UserProperty()
    text = db.StringProperty(multiline=True)
    conver = db.ReferenceProperty(Conver)
    created = db.DateTimeProperty(auto_now_add=True)
