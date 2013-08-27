from django.conf.urls import patterns, url

from betting import views

urlpatterns = patterns('',
    url(r'^bets$',                             views.mybets), 
    url(r'^bets/remove_bet/(?P<bet_id>\d+)/$', views.remove_bet),
    url(r'^bets/cancel_bet/(?P<bet_id>\d+)/$', views.cancel_bet),
    url(r'^bets/close_bet/(?P<bet_id>\d+)/$',  views.close_bet),
    url(r'^bets/decide_bet/(?P<bet_id>\d+)/(?P<side>\w)/(?P<password>\d+)/$', views.decide_bet),
    url(r'^bets/takeside_bet/(?P<bet_id>\d+)/(?P<side>\w)/$',                 views.takeside_bet),
    url(r'^bets/create_new/$',                 views.create_new),

) 
