from django.conf.urls import patterns, url

from matchmaking import views

import mm

urlpatterns = patterns('',
    url(r'^$',             views.landing,    name='landing'),
    url(r'^profile$',      views.profile,    name='logged-in'),
    url(r'^intro$',        views.intro,      name='intro'),
    
    # Matchmaking APIs
    url(r'^matchmaking/getplayerexp', mm.getplayerexp,  name='getplayerexp'),
    url(r'^matchmaking/startsearch$', mm.startsearch,   name='getmatch')
)