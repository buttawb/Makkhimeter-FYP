from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group

# Register your models here.

admin.site.register(w_dimen)
admin.site.register(w_shape)
admin.site.register(Wing_Image)
admin.site.register(Eye_Image)
admin.site.register(w_bristles)
admin.site.register(e_colour)
admin.site.register(e_dimension)
admin.site.register(e_ommatidium)

