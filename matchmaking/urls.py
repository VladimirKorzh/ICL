from django.conf.urls import patterns, url

from matchmaking import views

import mm

urlpatterns = patterns('',
    url(r'^$',             views.landing,    name='landing'),
    
    url(r'^intro$',        views.intro,      name='intro'),    
    url(r'^login$',        views.login,      name='login'),     
    url(r'^stacks$',       views.stacks,     name='stacks'),
    url(r'^ratings$',      views.ratings,    name='ratings'),
    url(r'^update_profile$',     views.update_profile, name='profile_update'),
)