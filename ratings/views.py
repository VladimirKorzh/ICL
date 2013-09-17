from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from matchmaking.models import Player
from datetime import tzinfo, datetime




@login_required 
def main(request):
      social_auth = request.user.social_auth.get(provider='steam')
      steamid     = social_auth.extra_data.get('steamid')  
      
      data = {'profile':Player.objects.get(uid=steamid)}
      
      players = Player.objects.all()  
      data['playerslist'] = []
      
      for each_player in players:
	  data['playerslist'].append({'nickname':    each_player.nickname,
				     'id': 	       each_player.id,
				     'extra_exp_pts': each_player.extra_exp_pts,
				     'rating':        each_player.exp+each_player.extra_exp_pts,
				     'uid':           each_player.uid,
				     'exp':           each_player.exp,
				     'last_updated':  get_time_elapsed(each_player)
				      })
			
      data['playerslist'] = sorted(data['playerslist'], key=lambda pl:pl['exp'], reverse=True)
	
      return render(request, 'ratings.html', data)