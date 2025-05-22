from django.contrib import admin
from .models import Articles
from .models import Comments


admin.site.register(Articles)
admin.site.register(Comments)