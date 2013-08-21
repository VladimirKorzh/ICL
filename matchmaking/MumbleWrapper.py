import Ice 
Ice.loadSlice("/usr/share/slice/Murmur.ice", ['-I'+ Ice.getSliceDir()])
import Murmur

class ICLMumble():
  """ Class is used for managing the Mumble server """
  def __init__(self):    
    # initialize Ice
    prop = Ice.createProperties()
    prop.setProperty("Ice.ImplicitContext", "Shared")
    idd = Ice.InitializationData()
    idd.properties = prop
    ice = Ice.initialize(idd)
    ice.getImplicitContext().put("secret", "1234567890")

    # Let Ice know where to go to connect to mumble
    proxy = ice.stringToProxy("Meta:tcp -p 6502")

    # Create a dynamic object that allows us to get a programmable interface for Mumble
    meta = Murmur.MetaPrx.checkedCast(proxy)

    # Get the server instance from the set of servers.    
    self.server   = meta.getServer(1)
    self.channels = self.server.getChannels()
    self.users    = self.server.getUsers()
                               
  def getChannelObj(self, value):
    """ Returns the channel object if there is one that has name or id
	equal to the passed value """
	
    channel = None    
    for chid in self.channels:
      if self.channels[chid].name == value or self.channels[chid].id == value:
	channel = self.channels[chid]
	return channel
	
    if channel == None:
      print "Error: Channel not found."
      return None

    
  def getUserObj(self, value):
    """ Returns the user object if there is one that has name or id
	equal to the passed value """
	
    user = None    
    for usid in self.users:
      if self.users[usid].name == value or self.users[usid].id == value:
	user = self.users[usid]
	return user
    
    if user == None:
      print "Error: User not found."
      return None

  def get_info(self):
	result = []
		
	for chid in self.channels:
	  channelinfo = {}	  
	  channelinfo['name']     = self.channels[chid].name
	  channelinfo['userlist'] = []	  
	  channelinfo['usernum']  = 0
	  result.append(channelinfo)
	  
	for usid in self.users:
	  user_channel_id   = self.users[usid].channel
	  user_channel_name = self.getChannelObj(user_channel_id).name
	  
	  for each in result:
	    if each['name'] == user_channel_name:
	      each['userlist'].append(self.users[usid].name)
	      each['usernum'] += 1

	for each in result:    
	  if each['usernum'] < 5:
	    while len(each['userlist']) < 5:
	      each['userlist'].append('.')

	print result          
	return result
      
      
      
      
      
      
      
      
      
      
      
      
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
	