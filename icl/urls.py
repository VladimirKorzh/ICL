from django.conf.urls import patterns, include, url
from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',    
    url(r'',                  include('social_auth.urls')),
    url(r'',                  include('matchmaking.urls')),
    
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    
    url(r'^logout$',         'django.contrib.auth.views.logout', {'next_page': '/intro'}),
    
    
    url(r'^admin/doc/',        include('django.contrib.admindocs.urls')),
    url(r'^admin/',            include(admin.site.urls)),
)
