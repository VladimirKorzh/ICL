import Ice 
Ice.loadSlice("/usr/share/slice/Murmur.ice", ['-I'+ Ice.getSliceDir()])
import Murmur
import sys, string, random, json

from django.conf import settings
from django.http import HttpResponse

from matchmaking.models import Player, Lobby, Roles, Search

# MUMBLE WRAPPER
class ICLMumble():
  def __init__(self):    
    # initialize Ice
    prop = Ice.createProperties()
    prop.setProperty("Ice.ImplicitContext", "Shared")
    idd = Ice.InitializationData()
    idd.properties = prop
    ice = Ice.initialize(idd)
    ice.getImplicitContext().put("secret", "@ED5adbd4f")

    # Let Ice know where to go to connect to mumble
    proxy = ice.stringToProxy("Meta:tcp -p 6502")

    # Create a dynamic object that allows us to get a programmable interface for Mumble
    meta = Murmur.MetaPrx.checkedCast(proxy)

    # Get the server instance from the set of servers.    
    self.server   = meta.getServer(1)
    self.channels = self.server.getChannels()
    self.users    = self.server.getUsers()
        
  def getChannelIdFromName(self, name):
    channel = None
    
    for chid in self.channels:
      if self.channels[chid].name == name:
	channel = self.channels[chid].id
	break
	
    if channel == None:
      print "Error: Channel not found."
      #sys.exit(1)
	
    return channel

  def getChannelNameFromId(self, idc):
    channelname = None
    
    for chid in self.channels:
      if self.channels[chid].id == idc:
	channelname = self.channels[chid].name
	break
    
    if channelname == None:
      print "Error: Channel not found."
      #sys.exit(1)

    return channelname
    
    
  def getUserIdFromName(self, name):
    user = None
    
    for usid in self.users:
      if users[usid].name == name:
	user = users[usid].id
	break
    
    if user == None:
      print "Error: User not found."
      #sys.exit(1)
    
    return user

  def createNewChannel(self, parentchannelname, channelname):
    parent = self.getChannelIdFromName(parentchannelname)
    self.server.addChannel(channelname, parent.id)
    
  def moveUser2Channel(self, username, channelname):
    channel = self.getChannelIdFromName(channelname)
    user    = self.getUserIdFromName(username)
    
    user.channel = channel.id
    self.server.setState(user)    
    
  def deleteChannelbyName(self, channelname):
    channel = self.getChannelIdFromName(channelname)
    self.server.removeChannel(channel.id)

  def refresh(self):      
    # clean empty mumble channels except for AFK
    mumble_used_channel_ids_list = [self.users[i].channel for i in self.users]
    mumble_total_channel_ids_list = [i.id for i in self.channels.values()]
    print 'Used channel ids:',  mumble_used_channel_ids_list
    print 'Total channel ids:', mumble_total_channel_ids_list
    
    for each in self.channels.values():
      if each.id not in mumble_used_channel_ids_list:
	if each.id == self.getChannelIdFromName("Root"): continue
	print self.getChannelNameFromId(each.id), 'is removed: no users'
	self.server.removeChannel(each.id)
	
    # refresh local list
    self.channels = self.server.getChannels()	
    
    mumble_users_list     = [self.users[each] for each in self.users]    
    db_lobbys_names       = [i.name for i in Lobby.objects.all()]
    mumble_channels_names = [self.channels[i].name for i in self.channels]
       
    # create those that are not in db
    for each in mumble_channels_names:
      if each not in db_lobbys_names:
	newLobby = Lobby(name=each)
	newLobby.save()
	
    # delete unused channels in db
    for each in db_lobbys_names:
      if each not in mumble_channels_names:
	Lobby.objects.get(name=each).delete()
	
    # find players in Mumble and assign them to
    # the respective lobbies in db    
    for user in mumble_users_list:
      try:
	user_obj = Player.objects.get(nickname=user.name)	
	lookup_channel = self.getChannelNameFromId(user.channel)
	user_obj.lobby = Lobby.objects.get(name=lookup_channel)
	user_obj.save()
	  
      except Player.DoesNotExist:
	self.server.kickUser(user.session, "You are not allowed to login directly to Mumble server without using WebAuth.")
	print user.name, 'is in Mumble, not using webauth. KICKED'
	
# END MUMBLE WRAPPER    
    
    
    
   
    
# Steam auth interraction here 

def getUserAvatarUrl(request):
  steam_api_key = settings.STEAM_API_KEY
  social_auth = request.user.social_auth.get(provider='steam')
  return social_auth.extra_data.get('avatarmedium')
  
def updateUserInfo(request):
  social_auth = request.user.social_auth.get(provider='steam')
  steamid = social_auth.extra_data.get('steamid')
  
  try:
    player = Player.objects.get(uid=steamid)
  except Player.DoesNotExist:
    player = Player()
    
  player.uid      = steamid
  player.nickname = str(request.user)
  player.avatar   = social_auth.extra_data.get('avatarmedium')
  
  #try:
    #afklobby = Lobby.objects.get(name='AFK')     
  #except Lobby.DoesNotExist:
    #afklobby = Lobby(name='AFK')
    #afklobby.save()
    
  #player.lobby = None
  
  # create roles for user
  if player.roles == None:
    roles = Roles()
    roles.save()
    player.roles = roles    
  
  player.save()
  print "Player logged in:", player

# End steam auth interraction  
  
  
  
  
  
  
  
def get_open_lobbys(data): #TODO
      # get all lobbys that are not full
      alllobbies = Lobby.objects.all()
      data['openlobbys'] = []
      for lobby_obj in alllobbies:
	if Player.objects.filter(lobby=lobby_obj).count() < 5:
	  if lobby_obj.name == "Root": continue
	  lobbyinfo = {'name':         lobby_obj.name,
		      'players_count': Player.objects.filter(lobby=lobby_obj).count(),
		      'players_list':  Player.objects.filter(lobby=lobby_obj).values('nickname')}
	  data['openlobbys'].append(lobbyinfo)
	  
      return data     

      
def _generate_id(size=6, chars=string.digits):#TODO  
  return ''.join(random.choice(chars) for x in range(size))
  
  
def startsearch(request):#TODO  
    response = {"HTTPRESPONSE":1}
    print "Searching for user:", request.user
    #print "all players:", Player.objects.all()
    
    player_asking = Player.objects.get( nickname=request.user ) 
    newsearch = Search( player=player_asking )
    newsearch.save()
      
    json_data = json.dumps(response)
    return HttpResponse(json_data, mimetype="application/json")	
  
  
def getmatch(request):#TODO  
    KORZH_DEBUG = True
    response = {}
    print "getmatch for:", request.user
    player_asking = Player.objects.get(nickname=request.user) 
    search        = Search.objects.get(player=player_asking)
    
    if len(search.response) or KORZH_DEBUG:
      response["HTTPRESPONSE"] = 1
      response["lobby"] = search.response
    else:
      response["HTTPRESPONSE"] = 0
      
    search.delete()
    
    json_data = json.dumps(response)
    return HttpResponse(json_data, mimetype="application/json")	  

  
    
    
