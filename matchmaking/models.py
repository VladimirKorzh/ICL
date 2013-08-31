from django.db import models
from django.forms import ModelForm

class Player(models.Model):
	uid      = models.CharField(max_length=40)

	nickname = models.CharField(max_length=40)
	avatar   = models.CharField(max_length=120)
	profile  = models.CharField(max_length=120)

	exp_total_games = models.PositiveSmallIntegerField(default=0)
	exp             = models.PositiveSmallIntegerField(default=0)
	exp_vh_games    = models.PositiveSmallIntegerField(default=0)
	exp_h_games     = models.PositiveSmallIntegerField(default=0)
	exp_n_games     = models.PositiveSmallIntegerField(default=0)
	extra_exp_pts   = models.PositiveSmallIntegerField(default=0)

	pri_role = models.CharField(max_length=8)
	alt_role = models.CharField(max_length=8)

	last_updated = models.DateTimeField(auto_now=True)

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
	
	carry    = models.ForeignKey(Player, related_name="carry")
	solomid  = models.ForeignKey(Player, related_name="solomid")
	offlane  = models.ForeignKey(Player, related_name="offlane")
	support1 = models.ForeignKey(Player, related_name="support1")
	support2 = models.ForeignKey(Player, related_name="support2")
		
	def __unicode__(self):
	  return str(self.name)
  
      