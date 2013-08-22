from django.db import models

class Player(models.Model):
	uid      = models.CharField(max_length=40)
	nickname = models.CharField(max_length=80)	
	avatar   = models.CharField(max_length=120)
	
	exp      = models.PositiveSmallIntegerField(default=0)
	last_seen= models.DateField(auto_now=True)
	
	
	## TODO lobby = AFK at start
	#roles = models.ForeignKey(Roles, null = True, related_name='playerroles')
	#lobby = models.ForeignKey(Lobby, null = True, related_name='playerlobby')
	
	
	def __unicode__(self):
	    string = '\nUid: '+str(self.uid)+'\nNickname: '+str(self.nickname)+'\nAvatar: '+str(self.avatar)
	    if self.roles:
	      string += '\nRoles: '+self.roles.__unicode__()
	    return string

class Lobby(models.Model):
	name = models.CharField(max_length=20)		
	
	def __unicode__(self):
	    return u"%s" % (self.name)
	    
	    
class ValveApiCounts(models.Model):
	date    = models.DateField()
	amount  = models.PositiveIntegerField()
			
	def __unicode__(self):
	    return u"%s %s" % (self.date, str(self.amount))
		

		
		
		
class Roles(models.Model):
	carry   = models.BooleanField(default=False)
	offlane = models.BooleanField(default=False)
	solomid = models.BooleanField(default=False)
	support = models.BooleanField(default=False)
	utility = models.BooleanField(default=False)
	
	def __unicode__(self):
	  string = '\n<Roles>\n1:'+str(self.carry)+'\n2:'+str(self.solomid)+'\n3:'+str(self.offlane)+'\n4:'+str(self.utility)+'\n5:'+str(self.support)
	  return string
	  
	  
class Search(models.Model):
      player = models.ForeignKey(Player)
      response = models.CharField(max_length=20)
      
      def __unicode__(self):
	return "Nickname: "+ self.player.nickname + " Response: " + self.response
      