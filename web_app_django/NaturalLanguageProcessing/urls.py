from django.conf.urls import patterns, include, url
from textdomain import views

from django.views.static import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Examples:
	url(r'^$', views.home, name='home'), #Fixed Bug during the start of the server (Shahab).
	
    url(r'^blacklist/$', views.blacklist, name='blacklist'),
    url(r'^sentence/$', views.sentence, name='sentence'),
	
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
	# Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/', include('textdomain.urls')),
)
