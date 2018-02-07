from django.contrib import admin
from models import CommunityService

class CommunityServiceAdmin(admin.ModelAdmin):
    fields = ['service_department', 'service_phone','service_address','service_office_hours','community']
    list_display = ['service_department', 'service_phone','service_address','service_office_hours','community']
    
admin.site.register(CommunityService, CommunityServiceAdmin)