
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from matchmaking.models import Player, Match1v1, Inventory, MatchInfo
from random import randint
import snippets, account

import json

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
def profile_search(request,query):
    # returns a json encoded list of usernames that start with
    # provided symbols
    response = {}
    response['userlist'] = []

    matching = Player.objects.filter(nickname__startswith=query)
    for each in matching:
      response['userlist'].append( each.nickname )
        
    return HttpResponse(json.dumps(response), content_type="application/json")
    
    
@login_required 
def global_rating(request):
    data = snippets.get_session_info(request)
    
    players = Player.objects.all()  
    data['playerslist'] = []
    
    for each_player in players:
        data['playerslist'].append({'nickname':      each_player.nickname,
                                    'id':            each_player.id,
                                    'extra_exp_pts': each_player.rating.extra_pts,
                                    'rating':        each_player.rating.skillrating+each_player.rating.extra_pts,
                                    'uid':           each_player.uid,
                                    'exp':           each_player.rating.skillrating,
                                      })
          
    data['playerslist'] = sorted(data['playerslist'], key=lambda pl:pl['exp'], reverse=True)
  
    return render(request, 'ratings.html', data)
    
    
@login_required  
def matches(request):
    data = snippets.get_session_info(request)
    data['matches'] = []
    data['matches'].extend( Match1v1.objects.all() )
      
    return render(request, 'matches.html', data)

@login_required  
def match1v1(request, id, msg=''):
    data = snippets.get_session_info(request)

    if id != '0':      
      data['match'] = Match1v1.objects.get(id__exact=id)  

    if request.method != 'POST':
      if msg != '':
        data['message'] = msg
      return render(request, '1v1match.html', data)
      
    if request.method == 'POST':
      
        if request.POST['action'] == 'refresh':
            msg = 'refreshed'
          
        if request.POST['action'] == 'cancel':
            data['match'].info.result = 3
            data['match'].info.save()
            data['match'].save()
            msg = 'match cancelled'
            
        if request.POST['action'] == 'ready':
            # check that all the fields are the same
            if data['match'].info.bet_size.common == int(request.POST['Common']) and \
                data['match'].info.bet_size.uncommon == int(request.POST['Uncommon']) and \
                data['match'].info.bet_size.rare == int(request.POST['Rare']) and data['match'].info.result==0:

                if data['profile'].inventory.common >= data['match'].info.bet_size.common and \
                    data['profile'].inventory.uncommon >= data['match'].info.bet_size.uncommon and \
                    data['profile'].inventory.rare >= data['match'].info.bet_size.rare:                     
                      
                      if data['match'].sidea == data['profile']:
                        data['match'].sideaready = True
                        msg += 'Ready!'
                      if data['match'].sideb == data['profile']:  
                        data['match'].sidebready = True
                        msg += 'Ready!'
                      data['match'].save()
                      
                else:
                  msg += data['profile'].nickname + ' not enough items in inventory'
                
                if data['match'].sideaready == True and data['match'].sidebready == True:
                    ok = True
                    msg += 'both players ready, trying to lock'
                    for player in [data['match'].sidea, data['match'].sideb]:
                        # Lets just make sure that the players have these items on their accounts
                        if player.inventory.common >= data['match'].info.bet_size.common and \
                            player.inventory.uncommon >= data['match'].info.bet_size.uncommon and \
                            player.inventory.rare >= data['match'].info.bet_size.rare:                                                       
                              pass
                        else:
                            msg += 'not enough items on lock for player ' + player.nickname
                            ok = False                            
                            if data['match'].sidea == data['profile']:
                              data['match'].sideaready = False
                              msg += 'te!'
                            if data['match'].sideb == data['profile']:  
                              data['match'].sidebready = False
                              msg += 'te!'
                            data['match'].save()
                    if ok:
                      msg += 'locking the match'
                      for player in [data['match'].sidea, data['match'].sideb]:
                          # if we got to here then both players are ok
                          account.db_player_inventory_action(player.id, 1, data['match'].info.bet_size.id)
                          # start the match
                          data['match'].info.result = 4
                          data['match'].info.save()
                else:
                  msg += 'Wait for other player to press ready'
            else:
              msg += 'Bet was updated, please review the bet and click ready'
              
        if request.POST['action'] == 'create':
            if request.POST['sidea'] != '' and request.POST['sideb'] != '':
                sidea = Player.objects.get(nickname=request.POST['sidea'])
                sideb = Player.objects.get(nickname=request.POST['sideb'])
                common   = request.POST['Common']
                uncommon = request.POST['Uncommon']
                rare     = request.POST['Rare']
                
                if sidea != sideb:              
                    inv = Inventory()
                    inv.common = common
                    inv.uncommon = uncommon
                    inv.rare = rare
                    inv.save()                

                    matchinfo = MatchInfo()
                    matchinfo.sideapass = randint(1000, 9999)
                    matchinfo.sidebpass = randint(1000, 9999)
                    matchinfo.lobbypass = randint(1000, 9999)
                    matchinfo.bet_size  = inv
                    matchinfo.save()                                
                    
                    match = Match1v1()  
                    match.sidea = sidea
                    match.sideb = sideb
                    match.info  = matchinfo
                    match.save()
                    id = match.id
                    msg += 'Match created'
                else:
                    msg += 'Sides must be different players'
                            
        if request.POST['action'] == 'update':
            if data['match'].info.result == 0:
                data['match'].sideaready = False
                data['match'].sidebready = False
                data['match'].info.bet_size.common   = request.POST['Common']
                data['match'].info.bet_size.uncommon = request.POST['Uncommon']
                data['match'].info.bet_size.rare     = request.POST['Rare']
                data['match'].info.bet_size.save()
                data['match'].save()
                msg += 'Updated bet'
                
                
        if request.POST['action'] == 'winnerA' or request.POST['action'] == 'winnerB':
            # check for valid result and passwords
            if data['match'].info.result == 4:                         
                for hack in [{'side':1, 'pass':data['match'].info.sidebpass, 'winner':'winnerA', 'player': data['match'].sidea},
                             {'side':2, 'pass':data['match'].info.sideapass, 'winner':'winnerB', 'player': data['match'].sideb}]:
                             
                    if request.POST['action'] == hack['winner']:
                        if request.POST['pass'] != '':
                            if int(request.POST['pass']) == hack['pass']:
                                data['match'].info.result = hack['side'] 
                                data['match'].info.save()
                                
                                # award the winner twice the bet amount
                                account.db_player_inventory_action(hack['player'].id, 0, data['match'].info.bet_size.id)
                                account.db_player_inventory_action(hack['player'].id, 0, data['match'].info.bet_size.id)          
                            else:
                              msg += 'Wrong password'
          
    if msg != '':
      return redirect('/matches/1v1/'+str(id)+'/'+msg)
    else:
      return redirect('/matches/1v1/'+str(id))
