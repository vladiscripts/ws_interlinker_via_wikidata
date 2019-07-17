from django.db import models


# Create your models here.
class Region(models.Model):
    rid = models.IntegerField(primary_key=True, null=False)
    # rid = models.IntegerField(unique=True, null=False)
    name = models.CharField(max_length=128)


class Court(models.Model):
    cid = models.IntegerField(primary_key=True, null=False)
    # cid = models.IntegerField(unique=True, null=False)
    name = models.CharField(max_length=128)
    rid = models.IntegerField()
    # rid = models.ForeignKey(Region, to_field=Region.rid, on_delete='CASCADE')
