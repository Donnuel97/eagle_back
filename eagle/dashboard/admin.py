from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Admin)
admin.site.register(Agent)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Payments)
admin.site.register(Test)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('logo_header_color', 'navbar_color', 'sidebar_color')