
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from django.conf import settings
from matchmaking.models import Lobby, Player, Search


import mm, icl

def landing(request):
    if not request.user.is_authenticated():
	return redirect('/intro')
    else:
	return redirect('/profile')

def intro(request):
	server = icl.connect2server()
	users = server.getUsers()
	userlist = [users[i] for i in users]
	usernum = len(userlist)
		
	return render(request, 'matchmaking/intro.html', 
		      {'usernum':usernum, 'userlist':userlist, 'requestuser':request.user})  
@login_required
def profile(request):
	steam_api_key = settings.STEAM_API_KEY
	social_auth = request.user.social_auth.get(provider='steam')
	
	data = {'username':request.user, 'apikey': steam_api_key, 'steamid':social_auth.extra_data.get('steamid'), 'avatar':mm.getUserAvatarUrl(request)}
	
	data = mm.get_open_lobbys(data)

	mm.updateUserInfo(request)
	return render(request, 'matchmaking/profile.html', data)

