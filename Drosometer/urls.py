"""Drosometer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Droso import views
from django.conf import settings

from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.main),

    # Login Paths
    path('login', views.loginUser),
    path('logout', views.logoutUser),
    path('register', views.register_page),

    # Wing Paths
    path('w_dimen', views.wingdimen),
    path('w_dimen2', views.wingdimen2),
    path('w_shape', views.wingshape),
    path('w_shape2', views.wingshape2),
    path('w_bristles', views.wingbristles),
    path('w_bristles2', views.wingbristles2),
    path('bar', views.w_bar),
    path('opt', views.w_option),

    # Other paths
    path('aboutus', views.a_us),
    path('contactus', views.c_us),
    path('feedback', views.f_b),

    path('cropper_wing', views.cropper_bristles),
    path('cropper_eye', views.cropper_eye),

    # Eye Paths
    path('f_eye', views.eye_f),
    path('f_wing', views.wing_f),
    path('e_omat', views.eye_omat),
    path('e_omat2', views.eye_omat2),

    # path('f_thorax', views.thorax_f),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
