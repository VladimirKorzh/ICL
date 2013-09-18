
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from matchmaking.models import Player

import snippets, account

def landing(request):
    if not request.user.is_authenticated():
        return redirect('/intro')
    else:
        # fix for people reloading page after update has been released.
        return login(request)

def intro(request):
    data = snippets.get_session_info(request)
    return render(request, 'intro.html', data)  

def help(request, topic):
    # simply redirect user to the corresponding help page
    data = snippets.get_session_info(request)
      
    filename = str(topic) + '.html'
    return render(request, filename, data)
  
@login_required  
def login(request):
    data = snippets.get_session_info(request) 
    account.action_login(data)
    
    print "Player logged in:", data['personaname']
    return redirect('/stacks')
 
@login_required
def profile(request, profile_id):
    data = snippets.get_session_info(request)  
    data['me'] = Player.objects.get(uid=data['steamid'])
    data['pl'] = Player.objects.get(id__exact=profile_id)
    data['rt'] = data['pl'].rating
    data['inv']= data['pl'].inventory
    
    print data['personaname'],' is looking at profile ', data['pl'].nickname    
    return render(request,'profile_modal.html', data)

@login_required
def refresh_roles(request):
    data = snippets.get_session_info(request)      
    
    player_obj    = Player.objects.get(uid=data['steamid'])
    if request.method == 'POST':
        print 'Setting new player roles', request.POST['pri_role'], request.POST['alt_role'], 'for player', player_obj.nickname
        player_obj.pri_role = request.POST['pri_role']
        player_obj.alt_role = request.POST['alt_role']    
        player_obj.save()
        
    if request.method != 'POST':
      account.action_refresh_user_rating(data)
      
    return redirect('/stacks') 
    
@login_required
def refresh_rating(request):
    data = snippets.get_session_info(request)          
    account.action_refresh_user_rating(data)
      
    return redirect('/stacks')     
    
@login_required    
def check_skill(request):
    data = snippets.get_session_info(request)      
    
    if request.method == 'POST':
        steamid = request.POST['steamid']
        print data['personaname'],'is checking skill of', steamid
        account.action_check_user_skill(steamid)
        
    return redirect('/ratings')         
    
@login_required    
def take_items(request):
    data = snippets.get_session_info(request)
    account.action_inventory_take_items(data['steamid'])
    
    return redirect('/stacks') 

@login_required
def add_items(request):
    data = snippets.get_session_info(request) 
    account.action_inventory_add_items(data['steamid'])
    
    return redirect('/stacks') 

@login_required 
def global_rating(request):
    data = snippets.get_session_info(request)
    data['profile'] = Player.objects.get(uid=steamid)
    
    players = Player.objects.all()  
    data['playerslist'] = []
    
    for each_player in players:
        data['playerslist'].append({'nickname':    each_player.nickname,
                                    'id':            each_player.id,
                                    'extra_exp_pts': each_player.rating.extra_pts,
                                    'rating':        each_player.rating.skillrating+each_player.rating.extra_pts,
                                    'uid':           each_player.uid,
                                    'exp':           each_player.rating.skillrating,
                                      })
          
    data['playerslist'] = sorted(data['playerslist'], key=lambda pl:pl['exp'], reverse=True)
  
    return render(request, 'ratings.html', data)
    
@login_required  
def match(request):
    data = snippets.get_session_info(request)    
    return render(request, 'match.html', data)
      