# coding:utf-8
from django.db import models
import json
# Create your models here.

class OpinionRecord(models.Model):
    opinion_id      = models.AutoField(primary_key = True)
    opinion_type    = models.IntegerField(blank=True, null=True)
    opinion_content = models.TextField(blank = True, null = True)
    opinion_time    = models.TextField(blank = True, null = True)
    read_status     = models.IntegerField(blank=True, null=True)
    handle_type     = models.IntegerField(blank=True, null=True)
    community_id    = models.BigIntegerField(blank=True, null=True)
    user_id         = models.BigIntegerField(blank=True, null=True)
    
    class Meta:
        db_table="yl_opinion"

    def getPushRecordId(self):
        return self.opinion_id
    
    def toJSON(self):
        return to_json(self)
    
class ExceptionRecord(models.Model):
    er_id      = models.AutoField(primary_key = True)
    er_type    = models.IntegerField(blank=True, null=True) # android 0   ios  1
    er_content = models.TextField(blank = True, null = True)
    er_model   = models.TextField(blank = True, null = True)
    er_time    = models.TextField(blank = True, null = True)
    er_version = models.TextField(blank = True, null = True)
    
    class Meta:
        db_table="yl_exception"

    def getExceptRecordId(self):
        return self.er_id
    
    def toJSON(self):
        return to_json(self)
    
def to_json(obj):
    fields = []
    for field in obj._meta.fields:
        fields.append(field.name)
    d = {}
    for attr in fields:
        val = getattr(obj, attr)
        
        #如果是model类型，就要再一次执行model转json
        if isinstance(val, models.Model):
            val = json.loads(to_json(val))
        d[attr] = val
    return json.dumps(d)