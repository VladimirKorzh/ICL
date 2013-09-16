from django.db import models

from matchmaking.models import Player

class Stack(models.Model):
	name    = models.CharField(max_length=40)
	exp     = models.PositiveIntegerField(default=0, null=True)

	carry    = models.ForeignKey(Player, related_name="carry",    null=True)
	solomid  = models.ForeignKey(Player, related_name="solomid",  null=True)
	offlane  = models.ForeignKey(Player, related_name="offlane",  null=True)
	support1 = models.ForeignKey(Player, related_name="support1", null=True)
	support2 = models.ForeignKey(Player, related_name="support2", null=True)

	def __unicode__(self):
	  return str(self.name)