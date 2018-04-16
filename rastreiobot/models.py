from datetime import datetime

import mongoengine


class Package(mongoengine.Document):
    tracking_code = mongoengine.StringField()
    users = mongoengine.ListField()
    created_at = mongoengine.DateTimeField(default=datetime.utcnow)
    last_updated = mongoengine.DateTimeField()
