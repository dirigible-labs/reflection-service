from django.db import models
from django.contrib.auth.models import User


class UserToken(models.Model):
    fb_user_id = models.TextField(db_index=True)
    fb_access_token = models.TextField(db_index=True)
    user = models.ForeignKey(User)
