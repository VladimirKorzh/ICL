from django.db import models
 
class Hero(models.Model):
    # table that holds information about all
    # currently available heroes
    name = models.CharField(max_length=40)
    
class ValveApiCounts(models.Model):
    # A class that holds the information about the amount
    # of api calls that the application has made each day
    date    = models.DateField()
    amount  = models.PositiveIntegerField()
    
class Inventory(models.Model):
    # used to store items for betting and tournaments
    common   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    uncommon = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rare     = models.DecimalField(max_digits=5, decimal_places=2, default=0)

class Rating(models.Model):
    # total amount of games for the past 28 days
    month_games = models.PositiveSmallIntegerField(default=0)
    
    # calculated skill experience
    skillrating = models.PositiveSmallIntegerField(default=0)
    
    # amount of games in each skill rating
    veryhigh    = models.PositiveSmallIntegerField(default=0)
    high        = models.PositiveSmallIntegerField(default=0)
    normal      = models.PositiveSmallIntegerField(default=0)
    
    # extra games per month
    extra_pts = models.PositiveSmallIntegerField(default=0)  

    # total rating from matches
    matches_pts = models.PositiveSmallIntegerField(default=0)
    
    # last time when this table was refreshed
    last_updated = models.DateTimeField(auto_now=True)        
    
class Player(models.Model):
    # general player information that we get from valve
    uid      = models.CharField(max_length=40)
    nickname = models.CharField(max_length=80)
    
    # a nickname that could be used in mumble
    mumble_nickname = models.CharField(max_length=80)
    avatar          = models.CharField(max_length=120)

    # player defined roles   # 0 - Not set
    # 1 - Carry      # 2 - SoloMid
    # 3 - Offlane    # 4,5 - Support
    pri_role = models.PositiveSmallIntegerField(default=0)
    alt_role = models.PositiveSmallIntegerField(default=0)

    # pointers to various information structures
    inventory = models.ForeignKey(Inventory)
    rating    = models.ForeignKey(Rating)

class BotRequest(models.Model):
    # player that requested interraction
    player = models.ForeignKey(Player)
    
    # Interraction type # 1 - Reward  # 0 - Collect
    action = models.PositiveSmallIntegerField(default=0)
    
    # Are we done? Yes\No\Cancelled
    status = models.PositiveSmallIntegerField(default=0)
    
    # how many items does the person want to cash
    common = models.PositiveSmallIntegerField(default=0)
    uncommon = models.PositiveSmallIntegerField(default=0)
    rare = models.PositiveSmallIntegerField(default=0)
    
    # when was that request finished
    last_updated = models.DateTimeField(auto_now=True)
     
     
class MatchInfo(models.Model):
    # related inventory that holds bet information
    bet_size = models.ForeignKey(Inventory)
      
    # lobby password
    lobbypass = models.PositiveSmallIntegerField(default=0)
    
    # passwords for both sides
    sideapass = models.PositiveSmallIntegerField(default=0)
    sidebpass = models.PositiveSmallIntegerField(default=0)  

    # 0 - Not decided
    # 1 - Side A won the match  # 2 - Side B won the match
    # 3 - Cancelled             # 4 - In progress
    result = models.PositiveSmallIntegerField(default=0)                
 
class Match1v1(models.Model):
    # time this record was last modified, for rating purposes
    last_updated = models.DateTimeField(auto_now=True)
    
    # information about that match
    info = models.ForeignKey(MatchInfo)
    
    # which teams participate in this match
    sidea = models.ForeignKey(Player, null=True, related_name="side1")
    sideb = models.ForeignKey(Player, null=True, related_name="side2")
   
    # Handshake between opponents
    sideaready = models.BooleanField(default=False)
    sidebready = models.BooleanField(default=False)
    
    # heroes that players have chosen
    sideahero1 = models.ForeignKey(Hero, null=True, related_name="side1hero1")
    sideahero2 = models.ForeignKey(Hero, null=True, related_name="side1hero2")
    sidebhero1 = models.ForeignKey(Hero, null=True, related_name="side2hero1")
    sidebhero2 = models.ForeignKey(Hero, null=True, related_name="side2hero2")
    
    
    
    
    
    
    
    
    
    
  
class Bet(models.Model):
    # which player made the bet
    player = models.ForeignKey(Player)
    
    # which match is he betting on
    match1v1 = models.ForeignKey(Match1v1)
    #match5v5 = models.ForeignKey(Match5v5)
      
    common   = models.PositiveSmallIntegerField(default=0)
    uncommon = models.PositiveSmallIntegerField(default=0)
    rare     = models.PositiveSmallIntegerField(default=0)
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
     


class Tournament(models.Model):
    # a model that represents a tournament in db.
    # it holds all the information about the tournament,
    # its type and other meta information. 
    
    # date\time of tournament start
    datetime = models.DateTimeField()

    # is the tournament free to enter
    entrycommon   = models.PositiveSmallIntegerField(default=0)
    entryuncommon = models.PositiveSmallIntegerField(default=0)
    entryrare     = models.PositiveSmallIntegerField(default=0) 
    
    inventory = models.ForeignKey(Inventory)
    
class TournamentTeam(models.Model):
    # temporary team for the tournament
    tournament = models.ForeignKey(Tournament)

class PlayerParticipant(models.Model):
    # holds the information about the player-tournament relationships
    # basically holds all the registered players for tournament.
    player = models.ForeignKey(Player)  
    tournament = models.ForeignKey(Tournament)
    
    # ready?
    ready = models.BooleanField(default=False)
    
    # registration date\time
    last_updated = models.DateTimeField(auto_now=True)  
 
 


      