from django.db import models

from matchmaking.models import Player

class Bet(models.Model):  
      rarity      = models.CharField() 
      amount      = models.PositiveSmallIntegerField()
      
      # A - B - ?
      result      = models.CharField()
      
      # Open - Collecting - Ready - Awarding - Done
      status      = models.CharField()
            
      sideapass   = models.PositiveSmallIntegerField()
      sidebpass   = models.PositiveSmallIntegerField()
      
      owner       = models.ForeignKey(Player)


class Bidder(models.Model):      
      # OK - Collect - Award 
      status  = models.CharField()      
      side    = models.CharField()
      
      player  = models.ForeignKey(Player)
      bet     = models.ForeignKey(Bet)
      
      def __unicode__(self):
	    string = str(self.player.nickname)
	    return string	    