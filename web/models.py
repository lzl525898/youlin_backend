# coding:utf-8
from django.db import models
from addrinfo.models import Community,City
from ckeditor.fields import RichTextField
import json

class News(models.Model):
    
    new_id                 = models.AutoField(primary_key = True)
    new_title              = models.TextField(blank = True, null = True)
    new_source             = models.TextField(blank = True, null = True)
    new_introduce          = models.TextField(blank = True, null = True)
    pri_flag               = models.IntegerField(blank = True, null = True)
    new_content            = RichTextField(verbose_name="正文")
    new_small_pic          = models.TextField(blank = True, null = True)
    city                   = models.ForeignKey(City, related_name='new_city', blank=True, null=True, on_delete=models.SET_NULL)
    community              = models.ForeignKey(Community, related_name='new_community', blank=True, null=True, on_delete=models.SET_NULL)
    new_add_time           = models.TextField(blank = True, null = True)
    push_flag              = models.IntegerField(blank = True, null = True)
    
    
    class Meta:
        db_table = "yl_news"
    
    def getNewId(self):
        return self.new_id
    
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


class NewsPush(models.Model):
    push_id                = models.AutoField(primary_key = True)
    push_newIds            = models.TextField(blank = True, null = True)
    push_time              = models.TextField(blank = True, null = True)
    community              = models.ForeignKey(Community, related_name='newpush_community', blank=True, null=True, on_delete=models.SET_NULL)
    class Meta:
        db_table = "yl_newspush"  
        
        
class APK(models.Model):
    v_id            = models.AutoField(primary_key = True)
    v_name          = models.TextField(blank = True, null = True)
    v_size          = models.TextField(blank=True, null=True)
    v_url           = models.TextField(blank = True, null = True)
    v_force         = models.TextField(blank = True, null = True)
    v_function      = models.TextField(blank = True, null = True)
    v_bug           = models.TextField(blank = True, null = True)
    v_time          = models.TextField(blank = True, null = True)
    class Meta:
        db_table = "yl_apk"

    def getApkId(self):
        return self.v_id
    
    def toJSON(self):
        return to_json(self) 
    
class Subscription(models.Model):

    s_id      = models.AutoField(primary_key=True)
    s_name    = models.TextField(blank = True, null = True)
    s_url     = models.TextField(blank = True, null = True)
    s_type    = models.IntegerField(default=0, editable = False)  # 0 表示服务器      1 表示自申请
    city      = models.ForeignKey(City, related_name='s_city', blank=True, null=True, on_delete=models.SET_NULL)
    community = models.ForeignKey(Community, related_name='COOMMUNITY', blank=True, null=True, on_delete=models.SET_NULL)
        


    class Meta:
        db_table="yl_subscription"   
        
        
        
        
class Role(models.Model):

    r_id                  = models.AutoField(primary_key=True)
    r_name                = models.TextField(blank = True, null = True)
    r_describe            = models.TextField(blank = True, null = True)
    r_root                = models.TextField(blank = True, null = True)
 

    class Meta:
        db_table="yl_role"           
        
        
class WebUser(models.Model):

    u_id                     = models.AutoField(primary_key=True)
    u_name                   = models.TextField(blank = True, null = True)
    u_password               = models.TextField(blank=True, null=True)
    u_phone_number           = models.TextField(max_length=50, blank=True, null=True)
    u_state                  = models.TextField(blank = True, null = True)
    u_email                  = models.EmailField(blank=True, null=True)
    role                     = models.ForeignKey(Role, related_name='role_name', blank=True, null=True, on_delete=models.SET_NULL)
    city                     = models.ForeignKey(City, related_name='c_name', blank=True, null=True, on_delete=models.SET_NULL)
    community                = models.ForeignKey(Community, related_name='com_name', blank=True, null=True, on_delete=models.SET_NULL)        
        
   
    class Meta:
        db_table="yl_webuser"  
        
        
class YLife(models.Model):   
    yl_id                  = models.AutoField(primary_key=True)
    yl_title               = models.TextField(blank = True, null = True)
    yl_author              = models.TextField(blank = True, null = True)
    yl_date                = models.TextField(blank = True, null = True)
    yl_content             = RichTextField(verbose_name="正文")
    yl_avatar              = models.TextField(blank = True, null = True)
    yl_flag                = models.IntegerField(blank = True, null = True)
    
    class Meta:
        db_table="yl_yllife" 
        
    def toJSON(self):
        return to_json(self)     