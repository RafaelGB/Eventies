"""Eventies URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from accounts import views as accounts_views, forms
from events import views as events_views

urlpatterns = [
    url(r'^$', events_views.HomeView, name='home'),
    url(r'^admin/', admin.site.urls,name='admin'),#enlace integrado en django con interfaz para administrar contenido
#-------------------------------------------------------------------------------------------------------
    url(r'^signup/$', accounts_views.signup, name='signup'),#crear nueva cuenta
    url(r'^login/$', accounts_views.my_login,  name='login'),#loguearse
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),#cerrar sesion
#-------------------------------------------------------------------------------------------------------
    url(r'^reset/$',#formulario para recuperar la password
        auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt'
        ),
        name='password_reset'),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'),
#-------------------------------------------------------------------------------------------------------
    url(r'^account/password/$', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'),
        name='password_change'),
    url(r'^account/password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
        name='password_change_done'),
    url(r'^account/$', accounts_views.UserUpdateView.as_view(), name='my_account'),
#-------------------------------------------------------------------------------------------------------
    url(r'^event/(?P<pk>\d+)/$', events_views.EventObjectView.as_view(template_name='eventDetails.html'), name='eventDetails'),
    url(r'^eventFilter/$', events_views.EventFilterView.as_view(template_name='eventFilter.html'), name='eventFilter'),
    url(r'^newEvent/$', events_views.NewEvent, name='newEvent'),
    url(r'^updateEvent/(?P<pk>\d+)/$', events_views.EventUpdateView.as_view(), name='updateEvent'),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
