from django.conf.urls import patterns, url

from matchmaking import views

import mm

urlpatterns = patterns('',
    url(r'^$',             views.landing,    name='landing'),
    
    url(r'^intro$',        views.intro,      name='intro'),    
    url(r'^login$',        views.login,      name='login'), 
    url(r'^bets$',         views.bets,       name='bets'), 
    url(r'^stacks$',       views.stacks,     name='stacks'),
    url(r'^ratings$',      views.ratings,    name='ratings'),
    
    url(r'^bets/(?P<action>\w+)/(?P<bet_id>\d+)/$', views.bets, name='viewbet'),
    
    # Matchmaking APIs
    url(r'^ajax/recalculateexp', mm.recalculateexp,  name='recalculateexp'),
    #url(r'^matchmaking/getchannelsinfo$', mm.getchannelsinfo,   name='getchannelsinfo')
)