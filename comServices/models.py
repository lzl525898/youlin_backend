from django.db import models
from addrinfo.models import Community
from users.models import Admin

# Create your models here.
class CommunityService(models.Model):
    service_id           = models.AutoField(primary_key = True)
    service_department   = models.TextField(blank = True, null = True)
    service_phone        = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    service_address      = models.TextField(blank = True, null = True)
    service_office_hours = models.TextField(blank = True, null = True)
    community            = models.ForeignKey(Community, related_name='community', blank=True, null=True, on_delete=models.SET_NULL)
    creater              = models.ForeignKey(Admin, related_name='admin', blank=True, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table = "yl_community_services"
    
    def getCommId(self):
        return self.service_id

class WeatherPushRecord(models.Model):
    
    wpr_id     = models.AutoField(primary_key = True)
    wpr_detail = models.TextField(blank = True, null = True)
    zod_detail = models.TextField(blank = True, null = True)
    zod_info   = models.TextField(blank = True, null = True)
    wpr_time   = models.BigIntegerField(blank = True, null = True)
    community  = models.ForeignKey(Community, related_name='community_wpr', blank=True, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table = "yl_weather_push"
    
    def getWeatherPushId(self):
        return self.wpr_id