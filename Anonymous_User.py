import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Drosometer.settings')
django.setup()

from django.contrib.auth.models import User

user = User()

user.id = 9999
user.password = 'anonymous'
user.is_superuser = False
user.username = 'Anonymous'

user.save()
