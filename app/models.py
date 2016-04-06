import datetime
from flask import url_for
from app import db

class Headline(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    text = db.StringField(max_length=255, required=True)
    person = db.StringField(max_length=255, required=True)

    def __unicode__(self):
        return self.text

    meta = {
        'ordering': ['-created_at']
    }