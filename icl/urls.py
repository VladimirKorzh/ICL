from django.conf.urls import patterns, include, url
import settings

from matchmaking import views as mm
from ratings     import views as ratings
from stacks      import views as stacks

urlpatterns = patterns('',  

    # Login process
    url(r'^$',		mm.landing,    name='landing'),
    url(r'^intro$',	mm.intro,      name='intro'),  
    url(r'^login$',	mm.login,      name='login'),  
    url(r'^logout$', 	'django.contrib.auth.views.logout', {'next_page': '/intro'}),    
        
    url(r'^help/(?P<topic>.+)',	mm.help,      name='help_topics'),  
        
    # user profile page modal dialog
    url(r'^profile/(?P<profile_id>\d+)/$', mm.profile,   name='show_profile'), 
    url(r'^profile/refresh_roles$',   mm.refresh_roles,  name='refresh'),
    url(r'^profile/refresh_rating$',  mm.refresh_rating, name='refresh'),
    url(r'^profile/check_skill',      mm.check_skill, name='refresh'),
    
    url(r'^profile/inventory/take$',  mm.take_items, name='refresh'),
    url(r'^profile/inventory/add$',   mm.add_items,  name='refresh'),
    
    url(r'^match$',   mm.match,  name='match'),
    
    
    # Stacks application
    url(r'^stacks$',          				    stacks.main),
    url(r'^stacks/leave_current$',			    stacks.leave_current),
    url(r'^stacks/kick_afk',			        stacks.kick_afk),
    url(r'^stacks/msg/(?P<msg>.+)$',          stacks.main),
    url(r'^stacks/create$',				    stacks.create_new_stack),
    url(r'^stacks/delete_empty$',			    stacks.delete_empty),
    url(r'^stacks/join/(?P<stack_name>\w+)/(?P<role>\d)/$',  stacks.join),
    url(r'^stacks/leave/(?P<stack_name>\w+)/$',		stacks.leave),
    url(r'^stacks/delete/(?P<stack_name>\w+)/$',		stacks.delete_stack),
    url(r'^stacks/voice/(?P<channel_name>.+)',                stacks.voice),
    url(r'^stacks/voice/',             			   stacks.voice),
            
    # Ratings
    url(r'^ratings$',          mm.global_rating,        		name='ratings'),
    
    # Steam authentification
    url(r'',                  include('social_auth.urls')),
    
    # Internationalization and translation
    url(r'^i18n/',            include('django.conf.urls.i18n')),
    
    # Serve files such as js, css, images
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),    
    
)
