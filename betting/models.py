from django.db import models

from matchmaking.models import Player

class Bet(models.Model):
      RESULT_CHOICES = (
		(u'A', u'Side A won'),
		(u'B', u'Side B won'),
		(u'NOTDECIDED', u'Not decided'),
      )
      
      STATUS_CHOICES = (
		(u'OPEN',       u'Bet is Open for new bidders'),
		(u'CLOSED',     u'Bet is Closed. No new bids are accepted'),
		
		(u'COLLECTING',  u'The bot is collecting items from bidders'),
		(u'COLLECTED',   u'The bot has finished collecting items from bidders'),
		
		(u'PRIZES',       u'Giving prizes to the winners'),
		(u'FINISHED',     u'Finished interraction. Nothing more to do.'),
      )
  
      item_rarity = models.CharField(max_length=20) 
      amount      = models.PositiveSmallIntegerField(default=1)
      result      = models.CharField(max_length=14, choices=RESULT_CHOICES)
      status      = models.CharField(max_length=14, choices=STATUS_CHOICES)
      
      
      sideapass   = models.PositiveSmallIntegerField(default=0)
      sidebpass   = models.PositiveSmallIntegerField(default=0)
      owner       = models.ForeignKey(Player)


class Bidder(models.Model):
      SIDE_CHOICES = (
	      (u'A', 'Side A'),
	      (u'B', 'Side B'),
      )
      
      STATUS_CHOICES = (
	      (u'COLLECTION', u'Waiting collection'),
	      (u'SUBMITTED',  u'Submitted items'),
	      (u'PRIZES',     u'Waiting for prizes'),
	      (u'DONE',       u'Interraction complete'),
      )
      
      side    = models.CharField(max_length=2, choices=SIDE_CHOICES)      
      status  = models.CharField(max_length=2, choices=STATUS_CHOICES)
      
      player  = models.ForeignKey(Player)
      bet     = models.ForeignKey(Bet)
      
      def __unicode__(self):
	    string = str(self.player.nickname)
	    return string	    