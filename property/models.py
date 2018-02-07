# coding:utf-8
from django.db import models
from addrinfo.models import Community
from users.models import Admin
import json

# Create your models here.
class PropertyInfo(models.Model):
    info_id               = models.AutoField(primary_key = True)
    name           = models.TextField(blank = True, null = True)
    phone          = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    address        = models.TextField(blank = True, null = True)
    office_hours   = models.TextField(blank = True, null = True)
    sender_id              = models.BigIntegerField(blank = True, null = True)
    community_id           = models.BigIntegerField(blank = True, null = True)
    
    class Meta:
        db_table = "yl_property_info"
    
    def getInfoId(self):
        return self.info_id
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
