

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from matchmaking import MumbleWrapper
from matchmaking.models import Player
from stacks.models import Stack

from random import randint

@login_required
def main(request):
      social_auth = request.user.social_auth.get(provider='steam')
      steamid     = social_auth.extra_data.get('steamid')     
      
      data = {'profile': Player.objects.get(uid=steamid),
	      'stacks' : Stack.objects.all(),
	      }
      for each in data['stacks']:
	check_for_afk(each)
	
      return render(request, 'stacks.html', data)
       
def same_exp_range(player_exp, stack_exp):
  if player_exp > stack_exp:    
    return True
    
  if player_exp < stack_exp:
    result = (stack_exp - player_exp) <= 75    
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
  return stack
       
def has_slot_for_player(player, stack):
  result = False

  if (player.pri_role == 'Carry' or player.alt_role == 'Carry') and stack.carry == None:
    result = True    
  if (player.pri_role == 'Solo Mid' or player.alt_role == 'Solo Mid') and stack.solomid == None:
    result = True
  if (player.pri_role == 'Offlane' or player.alt_role == 'Offlane') and stack.offlane == None:
    result = True    
  if (player.pri_role == 'Support' or player.alt_role == 'Support') and (stack.support1 == None or stack.support2 == None):
    result = True
    
  return result
       
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
       
def create_new_stack():
  newstack = Stack()
  newstack.name = "Temp"+str(randint(100,999))  
  newstack.save()
  newstack.name = "Stack" + str(newstack.id)
  
  mumble = MumbleWrapper.ICLMumble()
  mumble.createNewChannel("Root", newstack.name)
  mumble.destroy()
  newstack.channel = newstack.name
  newstack.save()
  return newstack
       
def delete_stack(stack):       
  mumble = MumbleWrapper.ICLMumble()
  mumble.deleteChannel(stack.name)
  mumble.destroy()  
  stack.delete()
       
def move_user_to_voice_channel(username, channelname):
  mumble = MumbleWrapper.ICLMumble()
  mumble.moveUser2Channel(username, channelname)
  mumble.destroy()
       
       
def check_in_mumble(mumble, player):
  user = mumble.getUserObj(player.mumble_nickname)
  if user == None:
    # not in mumble -> kick that guy.
    print 'kick', player.mumble_nickname
    return False
  else:
    # in mumble, check which channel and kick if in AFK
    ch = mumble.getChannelObj(user.channel)
    if ch == mumble.getChannelObj("AFK"):
      return False

  return True
  
def check_for_afk(stack):
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
  
  #if check_stack_empty(stack) == True:
    #delete_stack(stack)
    
  mumble.destroy()
       
@login_required
def voice(request, channel_name):
  social_auth = request.user.social_auth.get(provider='steam')
  steamid     = social_auth.extra_data.get('steamid')  
  username = Player.objects.get(uid=steamid).mumble_nickname
  move_user_to_voice_channel(username, channel_name)
  
  return redirect('/stacks')
       
@login_required       
def join(request, stack_name, role):
      social_auth = request.user.social_auth.get(provider='steam')
      steamid     = social_auth.extra_data.get('steamid')
      data = {'profile': Player.objects.get(uid=steamid)}    
      
      # make the player leave his current stack to prevent multiple entries
      # if he is currently in one       
      # don't delete the stack if he is switching roles within his stack
      if data['profile'].current_stack != '' and stack_name == data['profile'].current_stack:
	leave(request, data['profile'].current_stack, allow_delete=False)
            
      newstack = Stack.objects.get(name__exact=stack_name)
      
      if role == '1': 
	newstack.carry    = data['profile']
      if role == '2': 
	newstack.solomid  = data['profile']
      if role == '3': 
	newstack.offlane  = data['profile']
      if role == '4': 
	newstack.support1 = data['profile']
      if role == '5': 
	newstack.support2 = data['profile']
	
      recalc_stack_exp(newstack)
	
      newstack.save()
      data['profile'].current_stack = newstack.name
      data['profile'].save()
      
      move_user_to_voice_channel(data['profile'].mumble_nickname, newstack.name)
      
      return redirect('/stacks')

@login_required
def leave(request, stack_name, allow_delete=True):
      social_auth = request.user.social_auth.get(provider='steam')
      steamid     = social_auth.extra_data.get('steamid')
      player = Player.objects.get(uid=steamid)      
      stack = Stack.objects.get(name__exact=stack_name)            
      actually_left = False
      
      if stack.carry == player:
	stack.carry = None
	actually_left = True

      if stack.solomid == player:
	stack.solomid = None
	actually_left = True

      if stack.offlane == player:
	stack.offlane = None
	actually_left = True

      if stack.support1 == player:
	stack.support1 = None
	actually_left = True

      if stack.support2 == player:
	stack.support2 = None
	actually_left = True

      recalc_stack_exp(stack)      
      stack.save()
      
      if actually_left:
	player.current_stack = ''
	player.save()
      
      # if player has left the stack, kick him from voice channel
      if allow_delete == True:
	mumble = MumbleWrapper.ICLMumble()
	mumble.moveUser2Channel(player.mumble_nickname, "AFK")
	mumble.destroy()      
      
      # delete stack if there is no more people left in it
      if check_stack_empty(stack) and actually_left and allow_delete:	
	delete_stack(stack)

      return redirect('/stacks')
       
@login_required       
def find(request):
      social_auth = request.user.social_auth.get(provider='steam')
      steamid     = social_auth.extra_data.get('steamid')   
      data = {'profile': Player.objects.get(uid=steamid),
	      'stacks' : Stack.objects.all(),
	      }  
      matched = []
      
      # find stacks 
      for each in data['stacks']:
	  print each
	  # check if stack has slots for player
	  # and check if that matches his experience range
	  if same_exp_range(data['profile'].exp, each.exp) and has_slot_for_player(data['profile'], each):
	    matched.append(each)
            
      if len(matched):
	# we have stacks that match players experience,
	# let the player choose for himself
	data['stacks'] = matched
 
      else:
	# we don't have any stacks that match players experience
	# lets create a new one
	matched.append(create_new_stack())
	data['stacks'] = matched
	
      return render(request, 'stacks.html', data) 