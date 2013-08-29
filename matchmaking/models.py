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
		

class Stack(models.Model):
	name    = models.CharField(max_length=20)
	exp     = models.PositiveIntegerField(default=0)
	channel = models.CharField(max_length=40)
	
	carry   = models.ForeignKey(Player)
	solomid = models.ForeignKey(Player)
	offlane = models.ForeignKey(Player)
	support1 = models.ForeignKey(Player)
	support2 = models.ForeignKey(Player)
		
	def __unicode__(self):
	  return str(self.name)
  
      