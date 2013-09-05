from django.db import models

from matchmaking.models import Player

class Bet(models.Model):  
      rarity      = models.CharField(max_length=12) 
      amount      = models.PositiveSmallIntegerField()
      
      # A - B - ?
      result      = models.CharField(max_length=12)
      
      # Open - Collecting - Ready - Awarding - Done
      status      = models.CharField(max_length=12)
            
      sideapass   = models.PositiveSmallIntegerField(default=0)
      sidebpass   = models.PositiveSmallIntegerField(default=0)
      
      owner       = models.ForeignKey(Player)


class Bidder(models.Model):      
      # OK - Collect - Award 
      status  = models.CharField(max_length=12)      
      side    = models.CharField(max_length=12)
      
      player  = models.ForeignKey(Player)
      bet     = models.ForeignKey(Bet)
      
      def __unicode__(self):
	return u'%s %s' % (self.player.nickname, self.status)