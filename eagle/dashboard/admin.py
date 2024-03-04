from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Admin)
admin.site.register(Agent)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Payments)
