from django.contrib import admin
from .models import User
from .models import Admin

admin.site.register(User)
admin.site.register(Admin)
