from django.db import models

class Player(models.Model):
	uid      = models.CharField(max_length=40)
	nickname = models.CharField(max_length=80)	
	avatar   = models.CharField(max_length=120)
	
	exp      = models.PositiveSmallIntegerField(default=0)
	last_seen= models.DateTimeField(auto_now=True)		
	
	def __unicode__(self):
	    string = str(self.nickname)
	    return string

	    

	    
	    
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
      