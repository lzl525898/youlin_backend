from django.db import models
from users.models import User

# Create your models here. 
    
class PushRecord(models.Model):
    record_id     = models.AutoField(primary_key = True)
    community_id  = models.BigIntegerField(blank = True, null = True)
    pushType      = models.TextField(blank = True, null = True)
    contentType   = models.TextField(blank = True, null = True)
    #from_to       = models.TextField(blank = True, null = True)
    title         = models.TextField(blank = True, null = True)
    description   = models.TextField(blank = True, null = True)
    pushTime      = models.TextField(blank = True, null = True)
    user_id       = models.BigIntegerField(blank=True, null=True)
    customContent = models.TextField(blank = True, null = True)
    isClick       = models.IntegerField(blank=True, null=True)
    pushContent   = models.BigIntegerField(blank = True, null = True)
    
    class Meta:
        db_table="yl_pushRecord"

    
    def getPushRecordId(self):
        return self.record_id
 

    
    
    