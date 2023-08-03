from django.db import models

# Create your models here.


class User(models.Model):
    user_id = models.BigIntegerField()
    language = models.CharField(max_length=256, null=True)
    state = models.IntegerField()