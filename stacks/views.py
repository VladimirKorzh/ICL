

from django.shortcuts               import render, redirect
from django.contrib.auth.decorators import login_required

from matchmaking        import MumbleWrapper
from matchmaking.models import Player
from stacks.models      import Stack

from random import randint

@login_required
def main(request, msg=''):
  social_auth = request.user.social_auth.get(provider='steam')
  steamid     = social_auth.extra_data.get('steamid')     
  
  data = {'profile': Player.objects.get(uid__exact=steamid),
	  'stacks' : Stack.objects.all(),
	  }
	  
  if msg != '':
    data['message'] = msg
    print 'message appended', msg
    
  return render(request, 'stacks.html', data)

@login_required  
def create_new_stack(request):
  newstack = Stack()
  
  newstack.name = "Stack_"+str(randint(1000,9999))    
  
  while Stack.objects.filter(name__exact=newstack.name).exists():
    newstack.name = "Stack_"+str(randint(1000,9999))      
  
  mumble = MumbleWrapper.ICLMumble()
  mumble.createNewChannel("Root", newstack.name)
  mumble.destroy()
  newstack.save()
  
  message = 'Created stack: '+newstack.name
  return redirect('/stacks/msg/'+message)
  
@login_required
def delete_stack(request, stack_name): 
  message = ''
  stack = Stack.objects.get(name__exact=stack_name)
  if stack:      
    if check_stack_empty(stack):
      mumble = MumbleWrapper.ICLMumble()
      mumble.deleteChannel(stack.name)
      mumble.destroy()  
      name = stack.name
      stack.delete()      
      message = 'Deleted '+stack_name
    else:    
      message = stack_name + ' is not empty'
  else:
    message = 'Stack ' + stack_name + ' does not exist'
    
  return redirect('/stacks/msg/'+message)

    
@login_required
def voice(request, channel_name=''):
  if channel_name != '':
    social_auth = request.user.social_auth.get(provider='steam')
    steamid     = social_auth.extra_data.get('steamid')  
    username = Player.objects.get(uid__exact=steamid).mumble_nickname
    
    mumble = MumbleWrapper.ICLMumble()
    if mumble.getUserObj(username):
      mumble.moveUser2Channel(username, channel_name)
      message = 'Joined Voice Channel '+channel_name
    else:
      message = 'You need to launch mumble first'
    mumble.destroy()    
  else:
    message = 'You are not in a stack'
  return redirect('/stacks/msg/'+message)
         
         
         
@login_required       
def join(request, stack_name, role):
  social_auth = request.user.social_auth.get(provider='steam')
  steamid     = social_auth.extra_data.get('steamid')
  data = {'profile': Player.objects.get(uid__exact=steamid)}    
  
  message = ''
  
  joined = False
  
  if data['profile'].current_stack == '':
    newstack = Stack.objects.get(name__exact=stack_name)
    if newstack:        
      if role == '1' and newstack.carry == None: 
	newstack.carry    = data['profile']
	joined = True
      if role == '2' and newstack.solomid == None: 
	newstack.solomid  = data['profile']
	joined = True
      if role == '3' and newstack.offlane == None: 
	newstack.offlane  = data['profile']
	joined = True
      if role == '4' and newstack.support1 == None: 
	newstack.support1 = data['profile']
	joined = True
      if role == '5' and newstack.support2 == None: 
	newstack.support2 = data['profile']
	joined = True      
	
      if joined:
	newstack.save()
	recalc_stack_exp(newstack)
	data['profile'].current_stack = newstack.name
	data['profile'].save()	
	message = 'Joined '+stack_name
      else:
	message = 'Can not join this slot in ' + stack_name
    else:
      message = 'Stack does not exist'
  else:
    message = 'Leave your current stack first ('+data['profile'].current_stack+')'

  return redirect('/stacks/msg/'+message)

@login_required
def leave_current(request):
  social_auth = request.user.social_auth.get(provider='steam')
  steamid     = social_auth.extra_data.get('steamid')
  player      = Player.objects.get(uid__exact=steamid) 
  
  if player.current_stack != '':
    print player.nickname, 'is leaving his current stack', player.current_stack
    leave(request, player.current_stack, False)
    
  player.current_stack = ''
  player.save()
  return redirect('/stacks/msg/'+'Left the stack')
    
@login_required
def leave(request, stack_name, redirect_after=True):
  social_auth = request.user.social_auth.get(provider='steam')
  steamid     = social_auth.extra_data.get('steamid')
  player = Player.objects.get(uid__exact=steamid)      
  message = ''
    
  print 'Checking if stack exists'
  if Stack.objects.filter(name__exact=stack_name).exists():
    stack = Stack.objects.get(name__exact=stack_name)            
    left = False

    
    if stack:
      if stack.carry == player:
	stack.carry = None
	left = True

      if stack.solomid == player:
	stack.solomid = None
	left = True

      if stack.offlane == player:
	stack.offlane = None
	left = True

      if stack.support1 == player:
	stack.support1 = None
	left = True

      if stack.support2 == player:
	stack.support2 = None
	left = True   
	
      if left:
	stack.save()  
	recalc_stack_exp(stack)      
	message = 'You have left the stack'
      else:
	message = 'Can not leave stack '+stack_name
    else:
      message = 'Stack not found, cleaned your record'
      
    player.current_stack = ''
    player.save()
  else:
    message = 'Stack does not exist'
      
  if redirect_after:
    return redirect('/stacks/msg/'+str(message))

@login_required    
def delete_empty(request):
  mumble = MumbleWrapper.ICLMumble()  
  for each in Stack.objects.all():
    if each and check_stack_empty(each): 
	mumble.deleteChannel(each.name)  
	each.delete()
	print 'Deleted stack and channel for it', each.name
      
  mumble.channels = mumble.server.getChannels()
  mumble_used_channel_ids_list = [mumble.users[i].channel for i in mumble.users]
  mumble_total_channel_ids_list = [i.id for i in mumble.channels.values()]
  
  print 'Used channels', mumble_used_channel_ids_list
  print 'Total channels', mumble_total_channel_ids_list
  
  for each in mumble.channels.values():
    if each.id not in mumble_used_channel_ids_list:
      if each.id == mumble.getChannelObj("Root").id or each.id == mumble.getChannelObj("AFK").id or each.id == mumble.getChannelObj("Flood").id: continue
      mumble.deleteChannel(each.id)  
      print mumble.getChannelObj(each.id).name, 'is removed: no users'
         
  message = 'Deleted empty stacks and channels'  
  mumble.destroy()    
  return redirect('/stacks/msg/'+message)  
    
    

@login_required    
def kick_afk(request):
  mumble = MumbleWrapper.ICLMumble()  
  
  for each in Stack.objects.all():
    if each:
      check_for_afk(each)
  
  for each in mumble.users.values():
    if each.selfDeaf and each.selfMute and each.channel != mumble.getChannelObj("AFK").id:
      mumble.moveUser2Channel(each.name, "AFK")      
      pl = Player.objects.get(mumble_nickname__exact=each.name)
      if pl:
	if pl.current_stack != '':
	  stack = Stack.objects.get(name__exact=pl.current_stack)
	  if stack:
	    if stack.carry == pl:
	      stack.carry = None
	      left = True

	    if stack.solomid == pl:
	      stack.solomid = None
	      left = True

	    if stack.offlane == pl:
	      stack.offlane = None
	      left = True

	    if stack.support1 == pl:
	      stack.support1 = None
	      left = True

	    if stack.support2 == pl:
	      stack.support2 = None
	      left = True 
	    if left:
	      stack.save()
	      recalc_stack_exp(stack)
	    
	pl.current_stack = ''
	pl.save()
  
  mumble.destroy()
  message = 'Afk players were kicked'
  return redirect('/stacks/msg/'+message) 
  
    
    
def check_stack_empty(stack):
  result = True
      
  if stack.carry != None:
    result = False

  if stack.solomid != None:
    result = False

  if stack.offlane != None:
    result = False

  if stack.support1 != None:
    result = False

  if stack.support2 != None:
    result = False

  return result

def recalc_stack_exp(stack):
  total_exp = 0
  amount = 0
  for each in [stack.carry,stack.solomid,stack.offlane,stack.support1,stack.support2]:
    if each: 
      amount +=1
      total_exp += each.exp
      
  if amount != 0:
    stack.exp = total_exp / amount
  else:
    stack.exp = 0
  stack.save()         
         

def check_in_mumble(mumble, player):
  user = mumble.getUserObj(player.mumble_nickname)
  if user == None:
    # not in mumble -> kick that guy.
    print 'kick', player.mumble_nickname
    return False
  else:
    # in mumble, check which channel and kick if in AFK
    ch = mumble.getChannelObj(user.channel)
    
    if user.selfMute and user.selfDeaf:
      print 'kicking to afk'
      mumble.moveUser2Channel(player.mumble_nickname, "AFK")
      
    if ch == mumble.getChannelObj("AFK"):
      return False

  return True
  
  
def check_for_afk(stack):
  print 'checking for afk'
  mumble = MumbleWrapper.ICLMumble()  
  
  if stack.carry != None:
    if not check_in_mumble(mumble, stack.carry):
      stack.carry = None

  if stack.solomid != None:
    if not check_in_mumble(mumble, stack.solomid):
      stack.solomid = None

  if stack.offlane != None:
    if not check_in_mumble(mumble, stack.offlane):
      stack.offlane = None

  if stack.support1 != None:
    if not check_in_mumble(mumble, stack.support1):
      stack.support1 = None

  if stack.support2 != None:
    if not check_in_mumble(mumble, stack.support2):
      stack.support2 = None
  
  stack.save()      
  mumble.destroy()
         
  
  
  
  
  
  
  
  
  
  
  
#def same_exp_range(player_exp, stack_exp):
  #if player_exp > stack_exp:
    #return True
    
  #if player_exp < stack_exp:
    #result = (stack_exp - player_exp) <= 75
    #return result
       


       
       
       
       
       
#def has_slot_for_player(player, stack):
  #result = False

  #if (player.pri_role == 'Carry' or player.alt_role == 'Carry') and stack.carry == None:
    #result = True    
  #if (player.pri_role == 'Solo Mid' or player.alt_role == 'Solo Mid') and stack.solomid == None:
    #result = True
  #if (player.pri_role == 'Offlane' or player.alt_role == 'Offlane') and stack.offlane == None:
    #result = True    
  #if (player.pri_role == 'Support' or player.alt_role == 'Support') and (stack.support1 == None or stack.support2 == None):
    #result = True
    
  #return result
       



       


       



       
#@login_required       
#def find(request):
      #social_auth = request.user.social_auth.get(provider='steam')
      #steamid     = social_auth.extra_data.get('steamid')   
      #data = {'profile': Player.objects.get(uid=steamid),
	      #'stacks' : Stack.objects.all(),
	      #}  
      #matched = []
      
      ## find stacks 
      #for each in data['stacks']:
	  #print each
	  ## check if stack has slots for player
	  ## and check if that matches his experience range
	  #if same_exp_range(data['profile'].exp, each.exp) and has_slot_for_player(data['profile'], each):
	    #matched.append(each)
            
      #if len(matched):
	## we have stacks that match players experience,
	## let the player choose for himself
	#data['stacks'] = matched
 
      #else:
	## we don't have any stacks that match players experience
	## lets create a new one
	#matched.append(create_new_stack())
	#data['stacks'] = matched
	
      #return render(request, 'stacks.html', data) 