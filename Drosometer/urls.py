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

from django.urls import path, include
from Droso import views
from django.conf import settings
from Droso.views import loginUser
from django.conf.urls.static import static

from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView

from django.contrib.auth import views as auth_views

urlpatterns = [
                  path("admin/", admin.site.urls),
                  path('', views.main),

                  # Login Paths
                  path('login', loginUser),
                  path('logout', views.logoutUser),
                  path('register', views.register_page),

                  # Wing Paths
                  path('w_dimen', views.wingdimen),
                  path('bar', views.w_bar),
                  path('w_dimen2', views.wingdimen2),
                  path('details', views.detail_dimen),

                  path('w_shape', views.wingshape),
                  path('w_shape2', views.wingshape2),
                  path('w_shape_fb', views.shape_output),
                  path('out', views.shape_output),

                  path('w_bristles', views.wingbristles),
                  path('w_bristles2', views.wingbristles2),
                  path('cropper_wing', views.cropper_bristles),

                  path('f_eye', views.eye_f),
                  path('f_wing', views.wing_f),

                  # Other paths
                  path('aboutus', views.myteam),
                  path('contactus', views.c_us),
                  path('feedback', views.f_b),
                  # path('wing', views.wingfront),
                  # path('eye', views.eyefront),

                  # Eye Paths
                  path('e_omat', views.eye_omat),
                  path('e_omat2', views.eye_omat2),
                  path('cropper_eye', views.cropper_eye),

                  path('eye_col', views.eye_col),
                  path('col2', views.eye_col2),
                  path('e_c_o', views.eye_col_output),

                  path('e_dimen', views.eyedimen),
                  path('e_dimen2', views.eyedimen2),
                  path('e_d_o', views.e_dimen_out),

                  # Dashboard Paths
                  path('w_dashboard', views.wing_dashboard),
                  path('e_dashboard', views.eye_dashboard),

                  # path('f_thorax', views.thorax_f),

                  # path('check', views.fetch_data),

                  path('destructon', views.finalpage),

                  # path('password_reset/', auth_views.PasswordResetView.as_view(
                  #     template_name='templates/user/password_reset.html'), name='password_reset'),
                  # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
                  #     template_name='templates/user/password_reset_done.html'), name='password_reset_done'),
                  # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
                  #     template_name='templates/user/password_reset_confirm.html'), name='password_reset_confirm'),
                  # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
                  #     template_name='templates/user/password_reset_complete.html'), name='password_reset_complete'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
