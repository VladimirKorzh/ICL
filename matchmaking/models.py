from django.db import models

class Player(models.Model):
	uid      = models.CharField(max_length=40)
	nickname = models.CharField(max_length=80)	
	avatar   = models.CharField(max_length=120)
	
	exp      = models.PositiveSmallIntegerField(default=0)
	last_seen= models.DateTimeField(auto_now=True)		
	
	def __unicode__(self):
	    string = '\nUid: '+str(self.uid)+'\nNickname: '+str(self.nickname)
	    return string

	    
	    
# table used by betsbot 
class Bet(models.Model):
      RESULT_CHOICES = (
		(u'A', u'Side A won'),
		(u'B', u'Side B won'),
		(u'N', u'Not decided'),
      )
      
      STATUS_CHOICES = (
		(u'O', u'Open'),
		(u'C', u'Closed. Collecting items'),
		(u'P', u'In progress'),
		(u'D', u'Decided'),
		(u'R', u'Revoked'),
      )
  
      item_rarity = models.CharField(max_length=20) 
      amount      = models.PositiveSmallIntegerField(default=1)
      result      = models.CharField(max_length=2, choices=RESULT_CHOICES)
      status      = models.CharField(max_length=2, choices=STATUS_CHOICES)

# table used by betsbot 
class Better(models.Model):
      SIDE_CHOICES = (
	      (u'A', 'Side A'),
	      (u'B', 'Side B'),
      )
      STATUS_CHOICES = (
	      (u'P', u'Awaiting collection'),
	      (u'S', u'Submitted items'),
      )
      side    = models.CharField(max_length=2, choices=SIDE_CHOICES)      
      status  = models.CharField(max_length=2, choices=STATUS_CHOICES)
      
      player  = models.ForeignKey(Player)
      bet     = models.ForeignKey(Bet)
	    
	    
	    
class ValveApiCounts(models.Model):
	date    = models.DateField()
	amount  = models.PositiveIntegerField()
			
	def __unicode__(self):
	    return u"%s %s" % (self.date, str(self.amount))
		
		
		
		
		
		
		
		
#class Roles(models.Model):
	#carry   = models.BooleanField(default=False)
	#offlane = models.BooleanField(default=False)
	#solomid = models.BooleanField(default=False)
	#support = models.BooleanField(default=False)
	#utility = models.BooleanField(default=False)
	
	#def __unicode__(self):
	  #string = '\n<Roles>\n1:'+str(self.carry)+'\n2:'+str(self.solomid)+'\n3:'+str(self.offlane)+'\n4:'+str(self.utility)+'\n5:'+str(self.support)
	  #return string	  
      