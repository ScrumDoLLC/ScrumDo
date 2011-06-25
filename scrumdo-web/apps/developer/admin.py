from django.contrib import admin
from api.models import DeveloperApiKey, UserApiKey

class DeveloperKeyAdmin(admin.ModelAdmin):
    list_display = ('approved','developer', 'application_name', 'key')
    search_fields = ('application_name',)

admin.site.register(DeveloperApiKey , DeveloperKeyAdmin)

admin.site.register(UserApiKey)
