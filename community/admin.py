from django.contrib import admin
from models import Topic,Praise,Comment,Media_files,Activity,EnrollActivity,CollectionTopic

class TopicAdmin(admin.ModelAdmin):
    fields = ['topic_title', 'topic_content','sender_id','object_data_id','sender_community_id']
    list_display = ['topic_title', 'topic_content','sender_id','object_data_id','sender_community_id']
    
admin.site.register(Topic, TopicAdmin)

class ActivityAdmin(admin.ModelAdmin):
    fields = ['topic', 'startTime','endTime','location','tag']
    list_display = ['topic', 'startTime','endTime','location','tag']
    
admin.site.register(Activity, ActivityAdmin)

class EnrollActivityAdmin(admin.ModelAdmin):
    fields = ['activity', 'user','enrollUserCount','enrollNeCount']
    list_display = ['activity', 'user','enrollUserCount','enrollNeCount','enrollDate']
    
admin.site.register(EnrollActivity, EnrollActivityAdmin)

class CollectionTopicAdmin(admin.ModelAdmin):
    fields = ['user', 'topic','community_id']
    list_display = ['user', 'topic','community_id']
    
admin.site.register(CollectionTopic, CollectionTopicAdmin)