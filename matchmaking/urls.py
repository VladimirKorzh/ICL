from django.conf.urls import patterns, url

from matchmaking import views

import mm

urlpatterns = patterns('',
    url(r'^$',             views.landing,    name='landing'),
    
    url(r'^intro$',        views.intro,      name='intro'),    
    url(r'^login$',        views.login,      name='login'),     
    url(r'^stacks$',       views.stacks,     name='stacks'),
    url(r'^ratings$',      views.ratings,    name='ratings'),
    
    url(r'^bets$',                             views.mybets), 
    url(r'^bets/remove_bet/(?P<bet_id>\d+)/$', views.remove_bet),
    url(r'^bets/cancel_bet/(?P<bet_id>\d+)/$', views.cancel_bet),
    url(r'^bets/close_bet/(?P<bet_id>\d+)/$',  views.close_bet),
    url(r'^bets/decide_bet/(?P<bet_id>\d+)/(?P<side>\w)/(?P<password>\d+)/$', views.decide_bet),
    url(r'^bets/takeside_bet/(?P<bet_id>\d+)/(?P<side>\w)/$',                 views.takeside_bet),
    url(r'^bets/create_new/$',                 views.create_new),

    # Matchmaking APIs
    url(r'^ajax/recalculateexp', mm.recalculateexp,  name='recalculateexp'),
    #url(r'^matchmaking/getchannelsinfo$', mm.getchannelsinfo,   name='getchannelsinfo')
)