from django.contrib import admin
from .models import City
from .models import Community
from .models import BuildNum
from .models import AptNum
from .models import Block

class CityAdmin(admin.ModelAdmin):
    fields = ['city_name', 'city_code']

class CommunityAdmin(admin.ModelAdmin):
    fileds = ['community_name', 'community_code']

class BuildNumAdmin(admin.ModelAdmin):
    fileds = ['building_name']

class AptNumAdmin(admin.ModelAdmin):
    fileds = ['apt_name']

class BlockAdmin(admin.ModelAdmin):
    fileds = ['block_name']

admin.site.register(City, CityAdmin)
admin.site.register(Community, CommunityAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(BuildNum, BuildNumAdmin)
admin.site.register(AptNum, AptNumAdmin)
